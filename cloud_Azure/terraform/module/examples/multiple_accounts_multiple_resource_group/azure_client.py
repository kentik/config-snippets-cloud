import logging
import uuid
from dataclasses import dataclass
from typing import List

from azure.core.exceptions import AzureError
from azure.core.pipeline import PipelineContext, PipelineRequest
from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from azure.core.pipeline.transport import HttpRequest
from azure.identity import ClientSecretCredential, DefaultAzureCredential, InteractiveBrowserCredential
from azure.mgmt.authorization.v2020_04_01_preview import AuthorizationManagementClient
from azure.mgmt.authorization.v2020_04_01_preview.models import RoleAssignmentCreateParameters
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from msgraph.core import GraphClient
from msrest.authentication import BasicTokenAuthentication
from requests.exceptions import HTTPError

AZURE_OWNER_ROLE = "8e3af657-a8ff-443c-a75c-2fe8c4bcb635"
AZURE_READ_WRITE_ALL_PERMISSION = "1bfefb4e-e0b5-418b-a88f-73c46d2cc8e9"
MICROSOFT_GRAPH_API = "00000003-0000-0000-c000-000000000000"

log = logging.getLogger(__name__)


class AzureClientError(Exception):
    pass


def wrap_sdk_api_exceptions(msg: str = ""):
    """
    This is to handle the two separate Azure error hierarchies under AzureClientError:
    AzureSDK may raise AzureError
    MS Graph API may raise HTTPError
    """

    def outer(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (AzureError, HTTPError) as err:
                raise AzureClientError(msg) from err

        return inner

    return outer


@dataclass
class ServicePrincipal:
    app_id: str = ""
    secret: str = ""


@dataclass
class AppRegistration:
    obj_id: str
    principal: ServicePrincipal


@dataclass
class LoginCredentials:
    """
    Interactive (browser-based) login requires only tenant_id.
    Programatic login requires tenant_id and principal.
    In both cases, subscription_id can be selected automatically if not provided.
    """

    tenant_id: str
    subscription_id: str = ""
    principal: ServicePrincipal = ServicePrincipal()


class AzureClient:
    @classmethod
    def login_user(cls, tenant_id: str, subscription_id: str = ""):
        """Interactive (browser-based) login"""

        if tenant_id == "":
            raise AzureClientError("Failed to initialize client - tenant_id is required")

        cred = InteractiveBrowserCredential(tenant_id=tenant_id)
        return cls(cred, tenant_id, subscription_id)

    @classmethod
    def login_application(cls, lc: LoginCredentials):
        """Programmatic login"""

        if lc.tenant_id == "" or lc.principal.app_id == "" or lc.principal.secret == "":
            raise AzureClientError("Failed to initialize client - tenant_id and principal are required")

        cred = ClientSecretCredential(
            tenant_id=lc.tenant_id,
            client_id=lc.principal.app_id,
            client_secret=lc.principal.secret,
        )
        return cls(cred, lc.tenant_id, lc.subscription_id)

    def __init__(self, credentials, tenant_id: str, subscription_id: str = "") -> None:
        """
        If no subscription_id is provided, then auto-select is attempted
        """

        self._graph_client = GraphClient(credential=credentials)
        self._subscription_client = SubscriptionClient(credentials)
        self._tenant_id = tenant_id
        self._subscription_id = subscription_id or AzureClient._select_subscription_id(self._subscription_client)
        self._resource_client = ResourceManagementClient(credentials, self._subscription_id)
        self._auth_client = AuthorizationManagementClient(CredentialWrapper(credentials), self._subscription_id)
        self._check_credentials_working()
        log.debug("Initialized client with SubscriptionID '%s', TenantID '%s'", self._subscription_id, self._tenant_id)

    @staticmethod
    def _select_subscription_id(client: SubscriptionClient) -> str:
        subscription = next(client.subscriptions.list(), None)
        if subscription is None:
            raise AzureClientError("Failed to select SubscriptionID - no subscriptions available")

        subscription_id = subscription.subscription_id
        log.debug("Automatically selected Subscription ID: '%s'", subscription_id)
        return subscription_id

    def _check_credentials_working(self) -> None:
        try:
            next(self._subscription_client.subscriptions.list_locations(self.subscription_id), None)
        except AzureError as err:
            raise AzureClientError("Provided credentials are invalid") from err

    @property
    def tenant_id(self) -> str:
        return self._tenant_id

    @property
    def subscription_id(self) -> str:
        return self._subscription_id

    @wrap_sdk_api_exceptions("Failed to list locations")
    def list_locations(self) -> List[str]:
        locations = self._subscription_client.subscriptions.list_locations(self.subscription_id)
        names = [l.name for l in locations]
        return sorted(names)

    @wrap_sdk_api_exceptions("Failed to list resource groups")
    def list_resource_groups(self, location: str) -> List[str]:
        groups = self._resource_client.resource_groups.list()
        names = [g.name for g in groups if g.location == location]
        return sorted(names)

    @wrap_sdk_api_exceptions("Failed to list network security groups")
    def list_network_security_groups(self, resource_group: str) -> List[str]:
        FILTER = "resourceType eq 'Microsoft.Network/networkSecurityGroups'"

        groups = self._resource_client.resources.list_by_resource_group(resource_group, FILTER)
        names = [nsg.name for nsg in groups]
        return sorted(names)

    @wrap_sdk_api_exceptions("Failed to find app registrations")
    def find_app_registrations(self, name: str) -> List[str]:
        HEADERS = {"ConsistencyLevel": "Eventual", "Accept": "application/json"}

        query = f'/applications?$search="displayName:{name}"'
        result = self._graph_client.get(query, headers=HEADERS)
        result.raise_for_status()
        value = result.json()["value"]
        return [v["appId"] for v in value]

    @wrap_sdk_api_exceptions("Failed to create app registration")
    def create_app_registration(self, name: str) -> AppRegistration:
        HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

        ms_graph_id = self._ms_graph_object_id()

        # create AppRegistration
        required_access = [
            {
                "resourceAppId": MICROSOFT_GRAPH_API,
                "resourceAccess": [{"id": AZURE_READ_WRITE_ALL_PERMISSION, "type": "Role"}],
            }
        ]
        body = {
            "displayName": name,
            "requiredResourceAccess": required_access,
        }
        result = self._graph_client.post("/applications", json=body, headers=HEADERS)
        result.raise_for_status()
        result_dict = result.json()
        app_id = result_dict["appId"]
        app_object_id = result_dict["id"]

        # create ServicePrincipal
        body = {"appId": app_id}
        result = self._graph_client.post("/servicePrincipals", json=body, headers=HEADERS)
        result.raise_for_status()
        principal_id = result.json()["id"]

        # create ServicePrincipal secret
        result = self._graph_client.post(f"/servicePrincipals/{principal_id}/addPassword", headers=HEADERS)
        result.raise_for_status()
        principal_secret = result.json()["secretText"]

        # grant ReadWriteAll permission to ServicePrincipal
        body = {
            "principalId": principal_id,
            "resourceId": ms_graph_id,
            "appRoleId": AZURE_READ_WRITE_ALL_PERMISSION,
        }
        self._graph_client.post(f"/servicePrincipals/{ms_graph_id}/appRoleAssignedTo", json=body, headers=HEADERS)

        # create Owner RoleAssignment
        scope = f"/subscriptions/{self.subscription_id}/"
        guid = str(uuid.uuid4())
        role_id = f"/subscriptions/{self.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/{AZURE_OWNER_ROLE}"
        parameters = RoleAssignmentCreateParameters(
            role_definition_id=role_id,
            principal_id=principal_id,
            principal_type="ServicePrincipal",  # no retries needed in following requests thanks to this param
        )
        self._auth_client.role_assignments.create(scope=scope, role_assignment_name=guid, parameters=parameters)

        return AppRegistration(obj_id=app_object_id, principal=ServicePrincipal(app_id=app_id, secret=principal_secret))

    @wrap_sdk_api_exceptions("Failed to delete app registration")
    def delete_app_registration(self, app: AppRegistration) -> None:
        result = self._graph_client.delete(f"/applications/{app.obj_id}")
        result.raise_for_status()

    def _ms_graph_object_id(self) -> str:
        result = self._graph_client.get("/servicePrincipals")
        for sp in result.json()["value"]:
            if sp["appId"] == MICROSOFT_GRAPH_API:
                return sp["id"]
        raise AzureClientError("MS Graph API ServicePrincipal not found")


# Note: below helper class is copied from https://gist.github.com/lmazuel/cc683d82ea1d7b40208de7c9fc8de59d
class CredentialWrapper(BasicTokenAuthentication):
    def __init__(self, credential=None, resource_id="https://management.azure.com/.default", **kwargs):
        """
        Wrap any azure-identity credential to work with SDK that needs azure.common.credentials/msrestazure.
        Default resource is ARM (syntax of endpoint v2)
        :param credential: Any azure-identity credential (DefaultAzureCredential by default)
        :param str resource_id: The scope to use to get the token (default ARM)
        """
        BasicTokenAuthentication.__init__(self, None)
        if credential is None:
            credential = DefaultAzureCredential()
        self._policy = BearerTokenCredentialPolicy(credential, resource_id, **kwargs)

    @staticmethod
    def _make_request():
        return PipelineRequest(HttpRequest("CredentialWrapper", "https://fakeurl"), PipelineContext(None))

    def set_token(self):
        """Ask the azure-core BearerTokenCredentialPolicy policy to get a token.
        Using the policy gives us for free the caching system of azure-core.
        We could make this code simpler by using private method, but by definition
        I can't assure they will be there forever, so mocking a fake call to the policy
        to extract the token, using 100% public API."""
        request = self._make_request()
        self._policy.on_request(request)

        # Read Authorization, and get the second part after Bearer
        token = request.http_request.headers["Authorization"].split(" ", 1)[1]
        self.token = {"access_token": token}

    def signed_session(self, session=None):
        self.set_token()
        return super().signed_session(session)


# MANIAC = LoginCredentials(
#     subscription_id="a39991e5-fdc9-4fad-98ce-ec64c4f7e11d",
#     tenant_id="e0ae040b-2d16-41ad-bd29-faaa3ec975b9",
#     principal=ServicePrincipal(
#         app_id="277482eb-b69d-47ac-8f79-9b6065e63e8a", secret="Cek7Q~l6fnbeqxppqT3LbpKEW1IaZyjTd_pYI"
#     ),
# )


# POCZTA = LoginCredentials(
#     subscription_id="bda574ce-5d2e-4f4d-83da-0f7b0762e10c",
#     tenant_id="159cbdb4-6e26-4e6c-8920-f598249437e9",
# )


# if __name__ == "__main__":
#     # login as root and create ServicePrincipal
#     account = MANIAC
#     client = AzureClient.login_application(account)

#     groups = client.list_network_security_groups("dev-resource-group")
#     print(groups)
#     # scope = f"/subscriptions/{account.subscription_id}/"
#     # guid = str(uuid.uuid4())
#     # role_id = (
#     #     f"/subscriptions/{account.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/{AZURE_OWNER_ROLE}"
#     # )
#     # parameters = RoleAssignmentCreateParameters(
#     #     role_definition_id=role_id,
#     #     principal_id="0a82d416-fe45-4a0a-af34-8509a942cef9",
#     # )
#     # result = client._auth_client.role_assignments.create(scope=scope, role_assignment_name=guid, parameters=parameters)
#     # pprint(result.__dict__)

#     # client.subscriptions()

#     # sp = client.new_service_principal("TestPrincipalGRANTED")
#     # print(sp)

#     # # login as ServicePrincipal and list all  principals
#     # cred = AzureCredentials(
#     #     subscription_id=account.subscription_id,
#     #     tenant_id=account.tenant_id,
#     #     principal_id=sp.appId,
#     #     principal_secret=sp.secret,
#     # )
#     # client = AzureClient(cred)
#     # input("Press Enter to list principals...")
#     # # try:
#     # #     client.principals()
#     # # except Exception as err:
#     # #     print(err)

#     # pprint(client.find_service_principal("TestPrincipalGRANTED"))
#     # # delete application
#     # while True:
#     #     try:
#     #         client.delete_app(sp.appDeleteId)
#     #         break
#     #     except Exception as err:
#     #         print(err)
#     #         input("Press Enter to try again delete app...")
