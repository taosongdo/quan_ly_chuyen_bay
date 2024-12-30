from datetime import datetime
import hmac, hashlib, urllib.parse

url = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
return_url = "http://127.0.0.1:5000/VNP"
vnp_Secret = "JW5IDV48UYSCH2UDONDRNZF093E2YOJR"

vnp = {
    "vnp_Amount": None,
    "vnp_Command": "pay",
    "vnp_CreateDate": None,
    "vnp_CurrCode": "VND",
    "vnp_IpAddr": "127.0.0.1",
    "vnp_Locale": "vn",
    "vnp_OrderInfo": None,
    "vnp_OrderType": "VeMayBay",
    "vnp_ReturnUrl": return_url,
    "vnp_TmnCode": "UXV1MUSM",
    "vnp_TxnRef": None,
    "vnp_Version": "2.1.0"
}


def vnp_SecureHash(link, key):
    return hmac.new(key.encode("utf-8"), link.encode("utf-8"), hashlib.sha512).hexdigest()


def lay_url(tong_tien, thong_tin):
    vnp["vnp_CreateDate"] = str(datetime.now().strftime("%Y%m%d%H%M%S"))
    vnp["vnp_TxnRef"] = str(datetime.now().strftime("%H%M%S"))
    vnp["vnp_Amount"] = str(tong_tien * 100)
    vnp["vnp_OrderInfo"] = thong_tin

    link = ""
    for key in vnp:
        if vnp[key]:
            link += key + "=" + urllib.parse.quote_plus(vnp[key]) + "&"
    link = link[:-1]

    vnp_SH = vnp_SecureHash(link, vnp_Secret)
    link = url + '?' + '&'.join([f"{key}={urllib.parse.quote_plus(value)}" for key, value in vnp.items()])
    link += '&vnp_SecureHash=' + vnp_SH
    print(link)
    return link
