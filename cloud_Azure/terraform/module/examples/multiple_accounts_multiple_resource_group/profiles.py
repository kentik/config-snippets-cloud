import configparser
import logging
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

log = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes
@dataclass
class AzureProfile:
    name: str
    subscription_id: str
    tenant_id: str
    principal_id: str
    principal_secret: str
    location: str
    resource_group_names: List[str]
    storage_account_names: List[str]


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

    def field_not_set(field: str) -> bool:
        return getattr(profile, field) in ("", [])

    return list(filter(field_not_set, REQUIRED_AZURE_PROFILE_FIELDS))


def save_profiles(file_path: str, profiles: List[AzureProfile]) -> bool:
    config = configparser.ConfigParser()
    for profile in profiles:
        section = profile.name
        config.add_section(section)
        config[section]["subscription_id"] = profile.subscription_id
        config[section]["tenant_id"] = profile.tenant_id
        config[section]["principal_id"] = profile.principal_id
        config[section]["principal_secret"] = profile.principal_secret
        config[section]["location"] = profile.location
        config[section]["resource_group_names"] = ",".join(profile.resource_group_names)
        config[section]["storage_account_names"] = ""

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
    Raise RuntimeError on reading error/parsing error
    """

    config = configparser.ConfigParser()

    try:
        # note: config.read silently ignores the fact that file_path doesn't exist, resulting in empty config dict and no error reported
        config.read(file_path)
    except configparser.Error as err:
        raise RuntimeError() from err

    output_profiles: List[AzureProfile] = []
    available_profiles: List[str] = [p for p in config.keys() if p != "DEFAULT"]  # skip ini file "DEFAULT" section
    for profile_name in available_profiles:
        profile = config[profile_name]
        resource_groups, storage_accounts = get_resource_groups_and_storage_accounts(profile_name, dict(profile))
        azure_profile = AzureProfile(
            name=profile_name,
            subscription_id=profile.get("subscription_id", ""),
            tenant_id=profile.get("tenant_id", ""),
            location=profile.get("location", ""),
            resource_group_names=resource_groups,
            storage_account_names=storage_accounts,
            principal_id=profile.get("principal_id", ""),
            principal_secret=profile.get("principal_secret", ""),
        )
        output_profiles.append(azure_profile)

    log.info("Loaded %d profile(s) from '%s'", len(output_profiles), file_path)
    return output_profiles


def load_complete_profiles(file_path: str) -> List[AzureProfile]:
    """
    Read profiles from file; the profiles must have all the required fields set
    Return profile list on success
    Return empty list if file_path doesn't exist or file contains no profiles
    Raise RuntimeError on reading error/parsing error
    Raise ValueError for incomplete profiles
    """

    # load
    profiles = load_incomplete_profiles(file_path)

    # validate
    for profile in profiles:
        # check for missing required data
        missing_fields = list_missing_required_fields(profile)
        if missing_fields:
            missing_fields_str = ", ".join(missing_fields)
            raise ValueError(f"Profile '{profile.name}' is missing value for following fields: {missing_fields_str}")

    return profiles


def get_resource_groups_and_storage_accounts(name: str, profile: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    def split_names(names: str) -> List[str]:
        return [name.strip() for name in names.split(",")] if names else []

    # get resource groups and storage accounts
    resource_groups = split_names(profile.get("resource_group_names", ""))
    storage_accounts = split_names(profile.get("storage_account_names", ""))

    if storage_accounts == []:
        return (resource_groups, [])

    # if storage_accounts are specified, there should be a Storage Account name specified for every Resource Group name
    if len(storage_accounts) != len(resource_groups):
        print_log(
            f"In profile '{name}', 'storage_account_names' is specified but has different item count than 'resource_group_names'. Ignoring",
            file=sys.stderr,
            level=logging.WARNING,
        )
        return (resource_groups, [])

    # Storage Account names should meet Azure Storage Account naming restrictions
    def is_invalid_name(name: str) -> bool:
        return not is_valid_azure_storage_account_name(name)

    bad_names = filter(is_invalid_name, storage_accounts)
    bad_names_str = ", ".join(bad_names)
    if bad_names_str:
        print_log(
            f"Profile '{name}' contains invalid custom storage account names: '{bad_names_str}'. Ignoring custom names",
            file=sys.stderr,
            level=logging.WARNING,
        )
        return (resource_groups, [])

    return (resource_groups, storage_accounts)


def is_valid_azure_storage_account_name(name: str) -> bool:
    return 3 <= len(name) <= 24 and name.isalnum() and name.islower()


def print_log(msg: str = "", level: int = logging.INFO, file=sys.stdout) -> None:
    print(msg, file=file)
    log.log(level=level, msg=msg)


def print_profile(profile: AzureProfile) -> None:
    """Print the profile in a formatted manner"""

    for field in profile.__dataclass_fields__:
        value = getattr(profile, field)
        row = f"{field: >22} = {str(value)}"
        print(row)
