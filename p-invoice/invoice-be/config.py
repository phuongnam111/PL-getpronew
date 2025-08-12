class ProdConfig:
    #host
    invoice_host = 'https://kms.citigo.net/apis/einvoices/v2/accounts'
    invoice_account = 'https://kms.citigo.net/apis/einvoices/v2/accounts?partner={partner}&merchant_id={merchant_id}&merchant_code={merchant_code}'
    invoice_syncFromPartner = 'https://kms.citigo.net/apis/einvoices/v2/syncFromPartner?merchant_id={merchant_id}&merchant_code={merchant_code}&partner={partner}'
    invoice_gettemplate ='https://kms.citigo.net/apis/einvoices/v2/invoiceTemplates?merchant_id={merchant_id}&merchant_code={merchant_code}&partner={partner}&invoice_type=2'
    invoice_publishfrompos='https://kms.citigo.net/apis/einvoices/v2/invoices/publishFromPOS'
    invoice_getbatch='https://kms.citigo.net/apis/einvoices/v2/invoices/getBatch'
    invoice_publish_draft='https://kms.citigo.net/apis/einvoices/v2/invoices/publishDraft/batch'
    invoice_publish_bath='https://kms.citigo.net/apis/einvoices/v2/invoices/publishFromPOS/batch'
    
class Paramconfig:
    # invoice environment
    invoice_template_id ="e57f1fa9-7ea0-47c5-8884-660972257f58"
    invoice_serial ="2C24MTR"
    invoice_template_no ="1"
    apikey = 'bqx7odk6ey9m69m1kffa'
    merchant_id2=112000
    merchant_id = 113456  
    merchant_code = 'KFIN'
    partner = 'MISA'
    username = 'testlivekiotviet@yopmail.com'
    password = '12345678@Abc'
    tax_code = '0101243150-997'
    login_url = "https://4200241296-999-tt78democadmin.vnpt-invoice.com.vn"

    #publis invoice =>> with pos
    code="code000"
    ref_id="123456"
    invoice_name ='Hóa đơn GTGT'
    #invoice_datetime ='2024-08-08T11:18:09+07:00'
    currency_code ='VND'
    exchange_rate = 2
    invoice_note ='Ghi chú'
    payment_method_names = ['Thẻ']
    invoice_discount = 50000
    invoice_other_receivables = [
        {
            "name": "Thu khác A",
            "code": "code",
            "amount": 123456
        }
    ]
    items = [
        {
            "code": "item1",
            "type": 1,
            "desc": "ghi chú",
            "name": "Item 1",
            "unit_name": "hộp",
            "quantity": 1,
            "unit_price": 145455,
            "discount_rate": 0,
            "vat_rate": 0,
            "tax_type": 1  
        }

    ]
    buyer = {
        "legal_name": "VIỆN NGHIÊN CỨU NUÔI TRỒNG THUỶ SẢN II",
        "fullname": "VIỆN NGHIÊN CỨU NUÔI TRỒNG THUỶ SẢN",
        "tax_code": "0100109106-509",
        "address": "1A yet kieu",
        "code": "231231",
        "phone_number": "0986480048",
        "email": "23123@gmail.com",
        "bank_account": "312321312",
        "bank_name": "MB bank",
        "not_get_invoice": 0,
        "identification_code": "312313123321"
    }

    #publis invoice =>> with draft
    code="10000"
    ref_id="123456"
    invoice_name ='Hóa đơn GTGT'
    currency_code ='VND'
    exchange_rate = 2
    invoice_note ='Test'
    payment_method_names = ['Thẻ']
    invoice_discount = 161199999
    invoice_other_receivables_draft = [
        {
            "name": "phuong nam kfin",
            "code": "deep it",
            "amount": 165000000
        }
    ]
    items = [
        {
            "code": "item1",
            "type": 1,
            "desc": "ghi chú",
            "name": "Item 1",
            "unit_name": "hộp",
            "quantity": 1,
            "unit_price": 14540055,
            "discount_rate": 0,
            "vat_rate": 0,
            "tax_type": 0  
        },

          {
            "code": "item2",
            "type": 1,
            "desc": "ghi chú",
            "name": "Item 1",
            "unit_name": "hộp",
            "quantity": 1,
            "unit_price": 3415455,
            "discount_rate": 0,
            "vat_rate": 0,
            "tax_type": 0  
        },
           {
            "code": "item3",
            "type": 1,
            "desc": "ghi chú",
            "name": "Item 1",
            "unit_name": "hộp",
            "quantity": 1,
            "unit_price": 445455,
            "discount_rate": 0,
            "vat_rate": 0,
            "tax_type": 0  
        }

    ]
    buyer = {
        "legal_name": "kms",
        "fullname": "phuong nam vu",
        "tax_code": "0100109106-509",
        "address": "new mexico",
        "code": "001991",
        "phone_number": "0986480048",
        "email": "hand@gmail.com",
        "bank_account": "312321312",
        "bank_name": "VIB",
        "not_get_invoice": 1,
        "identification_code": "312313123321"
    }

  # Publish from Batch
    invoice_other_receivables_batch = [
        {
            "name": "Thu khác A",
            "code": "code",
            "amount": 123456
        }
    ]
    items = [
        {
            "code": "item1",
            "type": 1,
            "desc": "ghi chú",
            "name": "Item 1",
            "unit_name": "hộp",
            "quantity": 1,
            "unit_price": 145455,
            "discount_rate": 0,
            "vat_rate": 0
        },
        {
            "code": "item2",
            "type": 1,
            "desc": None,
            "name": "Item 2",
            "unit_name": "hộp",
            "quantity": 3,
            "unit_price": 272727,
            "discount_rate": 0,
            "vat_rate": 8
        },
        {
            "code": "item3",
            "type": 1,
            "desc": None,
            "name": "Item 3",
            "unit_name": "hộp",
            "quantity": 5,
            "unit_price": 636364,
            "discount_rate": 0,
            "vat_rate": 5
        },
        {
            "code": "item4",
            "type": 1,
            "desc": None,
            "name": "Item 4",
            "unit_name": "hộp",
            "quantity": 2,
            "unit_price": 145455,
            "discount_rate": 0,
            "vat_rate": 10
        },
        {
            "code": "item5",
            "type": 1,
            "desc": "ghi chú",
            "name": "Item 4",
            "unit_name": "hộp",
            "quantity": 1,
            "unit_price": 136364,
            "discount_rate": 0,
            "vat_rate": 0
        }
    ]
    buyer = {
        "legal_name": "VIỆN NGHIÊN CỨU NUÔI TRỒNG THUỶ SẢN II",
        "fullname": "VIỆN NGHIÊN CỨU NUÔI TRỒNG THUỶ SẢN",
        "tax_code": "0100109106-509",
        "address": "1A yet kieu",
        "code": "231231",
        "phone_number": "02343557351",
        "email": "23123@gmail.com",
        "bank_account": "312321312",
        "bank_name": "MB bank",
        "not_get_invoice": 1,
        "identification_code": "312313123321"
    }
    invoices = [
        {
            "code": "code 12",
            "ref_id": "{{ref_id}}1",
            "invoice_serial": "{{invoice_serial}}",
            "invoice_name": "Hóa đơn GTGT",
            "invoice_template_id": "{{invoice_template_id}}",
            "invoice_template_no": "{{invoice_template_no}}",
            "currency_code": "VND",
            "exchange_rate": 2,
            "invoice_note": "Ghi chú hóa đơn",
            "payment_method_names": ["Thẻ"],
            "invoice_discount": 50000,
            "invoice_other_receivables": [],
            "items": [
                {
                    "code": "item1",
                    "type": 1,
                    "desc": "ghi chú",
                    "name": "Item 1",
                    "unit_name": "hộp",
                    "quantity": 1,
                    "unit_price": 145455,
                    "discount_rate": 0,
                    "vat_rate": 0
                }
            ],
            "buyer": {
                "legal_name": "VIỆN NGHIÊN CỨU NUÔI TRỒNG THUỶ SẢN II",
                "fullname": "VIỆN NGHIÊN CỨU NUÔI TRỒNG THUỶ SẢN",
                "tax_code": "0100109106-509",
                "address": "1A yet kieu",
                "code": "231231",
                "phone_number": "0986480048",
                "email": "23123@gmail.com",
                "bank_account": "312321312",
                "bank_name": "MB bank",
                "not_get_invoice": 1,
                "identification_code": "312313123321"
            }
        }
    ]
    
