LOG_IN_URL_TEMPLATE = "{mailman_base_url}/admin/{list_name}"

MEMBERS_LIST_URL_TEMPLATE = "{mailman_base_url}/admin/{list_name}/members"
MODERATION_REQUESTS_URL_TEMPLATE = "{mailman_base_url}/admindb/{list_name}"
MODERATION_DETAILS_URL_TEMPLATE = (
    "{mailman_base_url}/admindb/{list_name}?msgid={message_id}"
)
ADD_MEMBERS_URL_TEMPLATE = "{mailman_base_url}/admin/{list_name}/members/add"
REMOVE_MEMBERS_URL_TEMPLATE = "{mailman_base_url}/admin/{list_name}/members/remove"
SYNC_MEMBERS_URL_TEMPLATE = "{mailman_base_url}/admin/{list_name}/members/sync"
SENDER_PRIVACY_URL_TEMPLATE = "{mailman_base_url}/admin/{list_name}/privacy/sender"
GENERAL_SETTINGS_URL_TEMPLATE = "{mailman_base_url}/admin/{list_name}/general"
ROSTER_URL_TEMPLATE = "{mailman_base_url}/roster/{list_name}"
