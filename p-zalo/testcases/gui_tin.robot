*** Settings ***
Suite Setup       Lay token kvs
Resource          ../core/api_kms.robot
Resource          ../env.robot
Library           ../python/webdriver_profile.py

*** Test cases ***
Thiet lap zalo sau do kiem tra ket noi
    [Tags]     not_run
    ${url_connect}=    Set Variable    ${URL_PUSBLISH}/message/zalo/connect?merchant_id=${MERCHANT_ID}&merchant_code=${MERCHANT_CODE}&partner=ZALO&token=${KVS_TOKEN}
    Log To Console    ${url_connect}
    connect_zalo_by_url    ${url_connect}    ${FIREFOX_PROFILE_FOLDER}
    Sleep    5s
    ${resp}=    API kiem tra trang thai ket noi ZOA
    Should Be Equal As Strings    ${resp['status']}    RECONNECTED

Lay danh sach template
    [Tags]     BE
    ${resp}=    API lay list template    ${MERCHANT_CODE}    ${MERCHANT_ID}
    Should Not Be Equal    ${resp['total']}    0

Kiem tra gui tin nhan thanh cong va tru tien
    [Tags]     BE
    ${OA_account}=    API lay thong tin OA account    ${MERCHANT_CODE}    ${MERCHANT_ID}    ${KVS_TOKEN}
    ${tien_truoc_gui_tin}=    Set Variable    ${OA_account['amount']}
    ${resp_gui_tin}=    API gui tin    ${TEMPLATE_ID_ZALO}    ${MERCHANT_ID}    ${MERCHANT_CODE}
    ${resp_status}=    API kiem tra trang thai gui tin    ${resp_gui_tin[0]['id']}
    Should Contain Any    ${resp_status[0]['status']}    DELIVERED    NEW
    ${OA_account}=    API lay thong tin OA account    ${MERCHANT_CODE}    ${MERCHANT_ID}    ${KVS_TOKEN}
    ${tien_sau_gui_tin}=    Set Variable    ${OA_account['amount']}
    ${tinh_tien_truoc_gui_tin}=    Evaluate    ${tien_truoc_gui_tin}-220
    Should Be Equal    ${tinh_tien_truoc_gui_tin}    ${tien_sau_gui_tin}

Xoa ket noi
    [Tags]     not_run
    ${resp}=    API Xoa ket noi
    Should Be Equal As Strings    ${resp['status']}    DISCONNECTED
