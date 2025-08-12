*** Settings ***
Resource          ../core/api_kms.robot
Resource          ../env.robot
Library           Selenium2Library
Library           ../python/webdriver_profile.py

*** Test cases ***
Gui tin trial
    [Tags]     BE
    [Setup]    Khoi tao gian hang moi va lay token kvs
    ${templates}=    API get trial templates
    ${resp}=    API gui tin trial    0328254662    ${templates[0]['template_id']}
    Should Not Be Empty    ${resp['message_id']}
    ${mess_info}=    API lay thong tin trial message    ${resp['message_id']}
    Should Contain Any    ${mess_info['status']}    WAIT_DELIVERED    DELIVERED
