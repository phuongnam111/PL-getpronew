*** Settings ***
Resource   ../env.robot
Library    Process
Library    Selenium2Library
*** Variables ***
${username_textbox}       //input[@id='UserName']
${password_textbox}       //input[@id='Password']
${login_button}           //input[@type='submit' and @value='Đăng nhập']
${list_retailer_menu}     //a[text()='List Retailers']


*** Keywords ***
Mo trinh duyet sang zalo
    # Open Browser   url=${URL_PUSBLISH}/message/zalo/connect?merchant_id=${MERCHANT_ID}&merchant_code=${MERCHANT_CODE}&partner=ZALO&token=${KVS_TOKEN}   browser=firefox   alias=None   remote_url=False   desired_capabilities=None    ff_profile_dir=C:\\Users\\Citigo\\AppData\\Local\\Mozilla\\Firefox\\Profiles\\ejycafrp.default-release-1723688727704   options=None   service_log_path=None
    # Open Browser   url=https://testz19.kiotviet.vn/man/#/DashBoard   browser=firefox   alias=None   remote_url=False   desired_capabilities=None    ff_profile_dir=C:\\Users\\Citigo\\AppData\\Local\\Mozilla\\Firefox\\Profiles   options=None  service_log_path=None
    Open Browser   url=https://testz19.kiotviet.vn/man/#/DashBoard   browser=firefox
    # Open Browser   ${URL_PUSBLISH}/message/zalo/connect?merchant_id=${MERCHANT_ID}&merchant_code=${MERCHANT_CODE}&partner=ZALO&token=${KVS_TOKEN}
    # ${res}=    Run Process  C:\\Users\\Citigo\\Downloads\\chrome-win64\\chrome.exe
    # Go To     url=https://testz19.kiotviet.vn/man/#/DashBoard

QLKV Dang nhap
    [Arguments]       ${username}     ${password}
    Open Browser   ${URL_QLKV}
    Input Text    ${username_textbox}    ${username}
    Input Text    ${password_textbox}    ${password}
    Click Button    ${login_button}
    Wait Until Element Is Visible    ${list_retailer_menu}

Lay Cookie tu QLKV
    [Arguments]       ${username}=${USERNAME_QLKV}     ${password}=${PASSWORD_QLKV}
    QLKV Dang nhap    ${username}    ${password}
    ${COOKIE}=     Get Cookies
    Log To Console    ${COOKIE}
    Set Global Variable    ${COOKIE_QLKV}    ${COOKIE}
    [Return]     ${COOKIE}

# *** Test cases ***
# Ket noi tai khoan Zalo
#     Mo trinh duyet sang zalo
#
# Test
#     Lay Cookie tu QLKV
