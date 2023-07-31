from fastapi import APIRouter
from controllers.mikrotik import connect_to_mikrotik, get_fidelis_addr, disabled_addr_in_mkt, add_comment_addr, add_addr_in_mkt_test, get_queues, sorted_queues, add_name, add_queue_in_mkt_test, get_firewall_addr_list, sorted_firewall_addr_list, add_comment_firewall_addr_list, add_firewall_addr_list_in_mkt_test, add_suspense_addr_list

router = APIRouter()

@router.get('/migration')
async def run_migration():
    data_fidelis = {'IP_MIKROTIK': '192.168.2.241'}
    data_test = {'IP_MIKROTIK': '192.168.2.238'}

    # Connect to MikroTik instances
    api_fidelis = await connect_to_mikrotik(data_fidelis)
    api_test = await connect_to_mikrotik(data_test)

    # # Get filtered IP addresses from Fidelis & add comment & disabled
    result_filtered = await get_fidelis_addr(api_fidelis)
    result_100 = result_filtered[-100:]

    await disabled_addr_in_mkt(result_100, api_fidelis)
    await add_comment_addr(result_100, api_fidelis)

    # Add filtered IP addresses to the test MikroTik instance
    await add_addr_in_mkt_test(api_test, result_100)


    # Get and add queues
    
    queue_filtered = await get_queues(api_fidelis)
    queue_100 = await sorted_queues(queue_filtered)
    await add_name(queue_100, api_fidelis)
    await add_queue_in_mkt_test(api_test, queue_100)


    # Get and add firewall address list & add comment
    
    firewall_addr_list = await get_firewall_addr_list(api_fidelis)
    firewall_addr_list_100 = await sorted_firewall_addr_list(firewall_addr_list)    
    await add_comment_firewall_addr_list(firewall_addr_list_100, api_fidelis)
    await add_firewall_addr_list_in_mkt_test(api_test, firewall_addr_list_100)
    await add_suspense_addr_list(api_test, firewall_addr_list, firewall_addr_list_100)
