*** Settings ***
Resource   ../env.robot

*** Keywords ***
API kiem tra trang thai ket noi ZOA
    [Arguments]   ${merchant_code}=RETAIL    ${merchant_id}=${MERCHANT_ID}   ${token}=${KVS_TOKEN}
    Create Session    mysesion    ${URL_PUSBLISH}
    ${headers}=    Create Dictionary     content-type=application/json    Authorization=${token}
    ${resp}=    Get Request    mysesion    /message/accounts/status?merchant_id=${merchant_id}&merchant_code=${merchant_code}&partner=ZALO&is_connecting=true    headers=${headers}
    Should Be Equal As Numbers    ${resp.status_code}    200
    Log    ${resp.json()}
    [Return]   ${resp.json()}

API lay thong tin OA account
    [Arguments]   ${merchant_code}=RETAIL    ${merchant_id}=${MERCHANT_ID}   ${token}=${KVS_TOKEN}
    Create Session    mysesion    ${URL_PUSBLISH}
    ${headers}=    Create Dictionary     content-type=application/json    Authorization=${token}
    ${resp}=    Get Request    mysesion    /message/accounts?merchant_id=${merchant_id}&merchant_code=${merchant_code}&partner=ZALO&is_connecting=true    headers=${headers}
    Should Be Equal As Numbers    ${resp.status_code}    200
    Log    ${resp.json()}
    [Return]   ${resp.json()}

API lay list template
    [Arguments]   ${merchant_code}=RETAIL    ${merchant_id}=${MERCHANT_ID}   ${token}=${KVS_TOKEN}
    Create Session    mysesion    ${URL_PRIVATE}
    ${headers}=    Create Dictionary     content-type=application/json    x-api-key=${X_API_KEY}
    ${resp}=    Get Request    mysesion    /message/templates/?merchant_id=${merchant_id}&merchant_code=${merchant_code}&partner=ZALO&page=1&limit=100    headers=${headers}
    Should Be Equal As Numbers    ${resp.status_code}    200
    Log    ${resp.json()}
    [Return]   ${resp.json()}

API gui tin
    [Arguments]     ${template_id}       ${merchant_id}=${MERCHANT_ID}      ${merchant_code}=RETAIL
    ${headers}=     Create Dictionary     content-type=application/json         x-api-key=${X_API_KEY}
    Create Session     mysession       ${URL_PRIVATE}
    ${body}=     Set Variable     {"merchant_id": ${merchant_id},"merchant_code": "${merchant_code}","partner": "ZALO","template_id": ${template_id},"campaign_name": "campaign_2","branch_id": 26,"messages": [{"phone": "0328254662","template_data": {"$zReqId": "$zReqId","Ten_Khach_Hang": "Ten_Khach_Hang","Ma_Hoa_Don": "Ma_Hoa_Don","$zReqTime": "$zReqTime","Ngay_Mua_Hang": "Ngay_Mua_Hang","Khach_Can_Tra": "Khach_Can_Tra","Hotline": "0123456789", "$z_oa_id_noised": "$z_oa_id_noised"}}]}
    ${resp}=    Post Request    mysession    /message/messages/publish    data=${body}    headers=${headers}
    Should Be Equal As Numbers    ${resp.status_code}    200
    Log   ${resp.json()}
    [Return]    ${resp.json()}

API gui tin trial
    [Arguments]    ${phone}    ${template_id}     ${merchant_id}=${MERCHANT_ID}      ${merchant_code}=RETAIL
    ${headers}=     Create Dictionary     content-type=application/json         x-api-key=${X_API_KEY}     Authorization=${KVS_TOKEN}
    Create Session    mysession    ${URL_PUSBLISH}
    ${body}=     Set Variable     {"merchant_id": ${merchant_id},"merchant_code": "${merchant_code}","partner": "ZALO","template_id": ${template_id},"phone": "${phone}"}
    ${resp}=    Post Request    mysession    /message/trial/messages    data=${body}    headers=${headers}
    Log   ${resp.json()}
    Should Be Equal As Numbers    ${resp.status_code}    200
    [Return]    ${resp.json()}

API lay ra tien KMA
    ${headers}=    Create Dictionary    content-type=application/json            Authorization=Bearer ${KVS_TOKEN}
    Create Session    mysession    ${URL_KMA}
    ${resp}=     Get Request    mysession   /v1/wallets/retrieveBalance     headers=${headers}
    Log   ${resp.json()}
    Should Be Equal As Numbers    ${resp.status_code}    200
    [Return]    ${resp.json()}

API get trial templates
    [Arguments]    ${merchant_id}=${MERCHANT_ID}      ${merchant_code}=RETAIL
    ${headers}=     Create Dictionary     content-type=application/json        Authorization=${KVS_TOKEN}
    Create Session    mysession    ${URL_PUSBLISH}
    ${resp}=     Get Request    mysession   /message/trial/templates?merchant_id=${merchant_id}&merchant_code=${merchant_code}&partner=ZALO     headers=${headers}
    Log   ${resp.json()}
    Should Be Equal As Numbers    ${resp.status_code}    200
    [Return]    ${resp.json()}

API kiem tra trang thai gui tin
    [Arguments]    ${track_id}       ${merchant_id}=${MERCHANT_ID}      ${merchant_code}=RETAIL
    ${headers}=    Create Dictionary    content-type=application/json            x-api-key=${X_API_KEY}
    Create Session    mysession    ${URL_PRIVATE}
    ${body}=     Set Variable     {"merchant_id":${merchant_id}, "merchant_code":"${merchant_code}","partner": "ZALO", "track_ids":["${track_id}"]}
    ${resp}=     POST Request    mysession   /message/messages/getBatch    data=${body}     headers=${headers}
    Log   ${resp.json()}
    Should Be Equal As Numbers    ${resp.status_code}    200
    [Return]    ${resp.json()}

API lay thong tin trial message
    [Arguments]    ${message_id}     ${merchant_id}=${MERCHANT_ID}      ${merchant_code}=RETAIL
    ${headers}=     Create Dictionary     content-type=application/json        Authorization=${KVS_TOKEN}
    Create Session    mysession    ${URL_PUSBLISH}
    ${resp}=     Get Request    mysession   /message/trial/messages/${message_id}/status?merchant_id=${merchant_id}&merchant_code=${merchant_code}&partner=ZALO    headers=${headers}
    Log   ${resp.json()}
    Should Be Equal As Numbers    ${resp.status_code}    200
    [Return]    ${resp.json()}

API Xoa ket noi
    [Arguments]      ${merchant_id}=${MERCHANT_ID}      ${merchant_code}=RETAIL
    ${headers}=     Create Dictionary     content-type=application/json        Authorization=${KVS_TOKEN}
    ${body}=     Set Variable    {"merchant_id": ${merchant_id},"merchant_code": "${merchant_code}","partner": "ZALO"}
    Create Session    mysession    ${URL_PUSBLISH}
    ${resp}=     PUT Request    mysession   /message/accounts/request-disconnect    data=${body}     headers=${headers}
    Log   ${resp.json()}
    Should Be Equal As Numbers    ${resp.status_code}    200
    [Return]    ${resp.json()}

# *** Testcases***
# Kiem tra trang thai ket noi ZOA
#     API kiem tra trang thai ket noi ZOA   ${MERCHANT_CODE}   ${MERCHANT_ID}   ${KVS_TOKEN}
#
#
# Lay thong tin OA account
#     API lay thong tin OA account    ${MERCHANT_CODE}   ${MERCHANT_ID}   ${KVS_TOKEN}
#
# Lay danh sach template
#     API lay list template    ${MERCHANT_CODE}   ${MERCHANT_ID}
#
# Gui tin
#     API gui tin      349368


# API get list template
#     [Arguments]    ${merchant_id}=${MERCHANT_ID}      ${merchant_code}=RETAIL
#     ${headers}=     Create Dictionary     content-type=application/json         x-api-key=${X-API-KEY}
#     Create Session    mysession    ${URL_PRIVATE}
#     ${resp}=     Get Request    mysession   /message/templates/?merchant_id=${merchant_id}&merchant_code=${merchant_code}&partner=ZALO&page=1&limit=100     headers=${headers}
#     Log   ${resp.json()}
#     Should Be Equal As Numbers    ${resp.status_code}    200
#     [Return]    ${resp.json()}
