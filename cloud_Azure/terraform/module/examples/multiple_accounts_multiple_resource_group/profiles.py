import configparser
import logging
from dataclasses import asdict, dataclass, field, fields
from typing import Any, Dict, List, Tuple, Type, TypeVar

log = logging.getLogger(__name__)


class ProfileConfigurationError(Exception):
    pass


class ProfilesInvalidError(ProfileConfigurationError):
    pass


class ProfilesIncompleteError(ProfileConfigurationError):
    pass


AzureProfileType = TypeVar("AzureProfileType", bound="AzureProfile")

# pylint: disable=too-many-instance-attributes
@dataclass
class AzureProfile:
    name: str = ""
    subscription_id: str = ""
    tenant_id: str = ""
    principal_id: str = ""
    principal_secret: str = ""
    location: str = ""
    resource_group_names: List[str] = field(default_factory=list)
    storage_account_names: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls: Type[AzureProfileType], data: Dict[str, Any]) -> AzureProfileType:
        # split List[str] type fields which are expected to be CSV
        for k in [f.name for f in fields(cls) if f.type == List[str] and f.name in data]:
            data[k] = [name.strip() for name in data[k].split(",") if name]

        return cls(**data)


def has_complete_authentication_data(p: AzureProfile) -> bool:
    return p.subscription_id != "" and p.tenant_id != "" and p.principal_id != "" and p.principal_secret != ""


def list_missing_required_fields(profile: AzureProfile) -> List[str]:
    """Return list of required fields that are not set in input profile"""

    REQUIRED_AZURE_PROFILE_FIELDS: List[str] = [
        "name",
        "subscription_id",
        "tenant_id",
        "principal_id",
        "principal_secret",
        "location",
        "resource_group_names"
        # storage_account_names is optional - names can be auto generated
    ]

    def field_not_set(field_name: str) -> bool:
        return getattr(profile, field_name) in ("", [])

    return list(filter(field_not_set, REQUIRED_AZURE_PROFILE_FIELDS))


def save_profiles(file_path: str, profiles: List[AzureProfile]) -> bool:
    config = configparser.ConfigParser()
    for profile in profiles:
        section = profile.name
        config.add_section(section)
        for k, v in asdict(profile).items():
            if isinstance(v, list):
                config[section][k] = ",".join(v)
            else:
                config[section][k] = v
    try:
        with open(file_path, "w", encoding="utf-8") as configfile:
            config.write(configfile)
        log.info("Saved profiles to '%s'", file_path)
        return True
    except OSError:
        log.exception("Failed to save profiles to '%s'", file_path)
        return False


def load_incomplete_profiles(file_path: str) -> List[AzureProfile]:
    """
    Read profiles from file; the profiles are allowed to have missing fields
    Return profile list on success
    Return empty list if file_path doesn't exist or file contains no profiles
    """

    config = configparser.ConfigParser()
    try:
        # note: config.read silently ignores the fact that file_path doesn't exist, resulting in empty config dict and no error reported
        config.read(file_path)
    except configparser.Error as err:
        raise ProfilesInvalidError(f"Failed to load '{file_path}'") from err

    return [AzureProfile.from_dict(dict(v)) for k, v in config.items() if k != "DEFAULT"]


def load_complete_profiles(file_path: str) -> List[AzureProfile]:
    """
    Read profiles from file; the profiles must have all the required fields set and valid
    Return profile list on success
    Return empty list if file_path doesn't exist or file contains no profiles
    """

    profiles = load_incomplete_profiles(file_path)

    for profile in profiles:
        validate_profile_configuration(profile)

    return profiles


def validate_profile_configuration(profile: AzureProfile) -> None:
    raise_on_missing_fields(profile)
    raise_on_invalid_storage(profile)


def raise_on_missing_fields(profile: AzureProfile) -> None:
    """check for missing required data"""

    missing_fields = list_missing_required_fields(profile)
    if missing_fields:
        missing_fields_str = ", ".join(missing_fields)
        msg = f"Profile '{profile.name}' is missing value for following fields: {missing_fields_str}"
        raise ProfilesIncompleteError(msg)


def raise_on_invalid_storage(profile: AzureProfile) -> None:
    """check for invalid storage accounts"""

    if profile.storage_account_names == []:
        return

    if len(profile.storage_account_names) != len(profile.resource_group_names):
        msg = f"In profile '{profile.name}', 'storage_account_names' is specified but has different item count than 'resource_group_names'"
        raise ProfilesInvalidError(msg)

    bad_names = list(filter(lambda name: not is_valid_azure_storage_account_name(name), profile.storage_account_names))
    if bad_names:
        bad_names_str = ", ".join(bad_names)
        msg = f"Profile '{profile.name}' contains invalid custom storage account names: '{bad_names_str}'"
        raise ProfilesInvalidError(msg)


def get_resource_groups_and_storage_accounts(profile: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    def split_names(names: str) -> List[str]:
        return [name.strip() for name in names.split(",")] if names else []

    # get resource groups and storage accounts
    resource_groups = split_names(profile.get("resource_group_names", ""))
    storage_accounts = split_names(profile.get("storage_account_names", ""))
    return (resource_groups, storage_accounts)


def is_valid_azure_storage_account_name(name: str) -> bool:
    return 3 <= len(name) <= 24 and name.isalnum() and name.islower()
