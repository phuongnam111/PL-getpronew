*** Settings ***
Library           BuiltIn
Library           Collections
Library           RequestsLibrary
Library           Selenium2Library
Library           String
Resource          core/api_kvs.robot
Resource          core/end2end.robot

*** variables ***
#confin DB môi trường STG
${BROWSER}             chrome
${URL_LOGIN_KVS}       https://api-man.kvpos.com
${URL_QLKV}            https://qlkv.kvpos.com/login?redirect=%2f#f=Unauthorized
${URL_PUSBLISH}        https://stg-kms.citigo.net
${URL_PRIVATE}         https://stg-kms-private.citigo.net
${URL_KMA}             https://portal-kma-stg.kvip.fun
${X_API_KEY}           lddgywwukokcygoh3uds1vlddvsiwd2qcogcp0y7mkiz6ckz
${TEMPLATE_ID_ZALO}    349307
${MERCHANT_ID}         12685
${RETAIL_CODE}         kvc301
${USERNAME}            admin
${PASSWORD}            123
${MERCHANT_CODE}       RETAIL
${KVS_TOKEN}       eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6InNCeCJ9.eyJpc3MiOiJrdnNzand0Iiwic3ViIjoyMDg2OCwiaWF0IjoxNzIzNTM3MjY3LCJleHAiOjE3MjU5NTY0NjcsInByZWZlcnJlZF91c2VybmFtZSI6ImFkbWluIiwicm9sZXMiOlsiVXNlciJdLCJrdnNvdXJjZSI6IlJldGFpbCIsImt2dXNldGZhIjowLCJrdndhaXRvdHAiOjAsImt2c2VzIjoiNTQzYjBmMmY3MTc0NGE3NmE2MTQ4NDE0NTEzYzE4MzMiLCJrdnVpZCI6MjA4NjgsImt2bGFuZyI6InZpLVZOIiwia3Z1dHlwZSI6MCwia3Z1bGltaXQiOiJGYWxzZSIsImt2dWFkbWluIjoiVHJ1ZSIsImt2dWFjdCI6IlRydWUiLCJrdnVsaW1pdHRyYW5zIjoiRmFsc2UiLCJrdnVzaG93c3VtIjoiVHJ1ZSIsImt2YmkiOiJUcnVlIiwia3ZjdHlwZSI6MiwidXNlQkkiOnsiQ3VzdG9tZXJCSVJlcG9ydF9SZWFkIjpbXSwiU2FsZUJJUmVwb3J0X1JlYWQiOltdLCJQcm9kdWN0QklSZXBvcnRfUmVhZCI6W10sIkZpbmFuY2VCSVJlcG9ydF9SZWFkIjpbXX0sImt2YmlkIjo1ODE5LCJrdnJpbmRpZCI6Miwia3ZyY29kZSI6Imt2YzMwMSIsImt2cmlkIjoxMjY4NSwia3Z1cmlkIjoxMjY4NSwia3ZyZ2lkIjoyLCJwZXJtcyI6IiJ9.Bq5_1PuP314JHTmH39HhNRAeDj2XL-4ouoWyQDyKGgXV25uAun5EewhXoYVAlwpZMBDYh2zCCK8lRVkDPfVLgcqEAqYM3RNZiUZSQ4XUikTZ4LCjbGRaBIRGukjYnOgH20xOvODhjCOo_Q49-d8CCQeymSjv3oU6fvcXZzT0GHcXqNkQTRXcVhaJkaLoi3Xk9ZFW6fCheRC9sJYamtYOtnNZQO9ZHfmuYPBCHDig9s-Dgc08U-Vxkn554gXh3bATFixHzuhALbH1sFVIgJNG2J0pmwMdy3N_vz1CugRtHp7jiHVv-dKGJRjT4kTXs4kQnZiejHSBZUblFQLyld3jPQ

# ${FIREFOX_PROFILE_FOLDER}      C://Users//giang.th2//AppData//Local//Mozilla//Firefox//Profiles//3dlq6v2j.default-release

${URL_QLKV_RETAIL}     https://qlkv.kvpos.com
${USERNAME_QLKV}       admin@kiotviet.com
${PASSWORD_QLKV}       123456

*** Keywords ***
Lay token kvs
    ${merchant_token}   API login KVS lay token KVS    ${RETAIL_CODE}    ${USERNAME}   ${PASSWORD}
    Set Global Variable    ${KVS_TOKEN}    ${merchant_token}

Khoi tao gian hang moi va lay token kvs
    QLKV Dang nhap    ${USERNAME_QLKV}    ${PASSWORD_QLKV}
    ${COOKIE}=     Get Cookies
    # Log To Console    ${COOKIE}
    Set Global Variable    ${COOKIE_QLKV}    ${COOKIE}
    ${new_merchant}    API tao gian hang KVS-retail
    Set Global Variable    ${MERCHANT_ID}    ${new_merchant['Retailer']['Id']}
    Set Global Variable    ${RETAIL_CODE}    ${new_merchant['Retailer']['Code']}
    ${new_merchant_token}   API login KVS lay token KVS    ${RETAIL_CODE}    ${USERNAME}   ${PASSWORD}
    Set Global Variable    ${KVS_TOKEN}    ${new_merchant_token}
    Close All Browsers
