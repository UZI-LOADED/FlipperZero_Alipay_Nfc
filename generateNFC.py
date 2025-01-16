from urllib.parse import quote

# Define the Alipay URL and append the necessary parameter
pay_url = "https://qr.alipay.com/fkx17629ee8clivc1hn8kc8"
if not pay_url.endswith('?noT=ntagtqp'):
    pay_url += '?noT=ntagtqp'

# Define fixed page data
fixed_pages = {
    'Page 0': '1D 6E 74 8F',
    'Page 1': '9A 95 00 00',
    'Page 2': '0F A3 FF FF',
    'Page 3': 'E1 10 3E 00',
    'Page 4': '03 FF 00 FF',
    'Page 5': '91 01 CE 55',
    'Page 130': 'FF FF FF BD',
    'Page 131': '00 00 00 04',
    'Page 132': '00 00 00 00',
    'Page 133': '00 00 00 00',
    'Page 134': '00 00 00 00',
}

# Define the URL to be inserted, starting from Page 6
scheme = f"alipay://nfc/app?id=10000007&actionType=route&codeContent={quote(pay_url, 'utf-8')}"
url = f"render.alipay.com/p/s/ulink/?scene=nfc&scheme={quote(scheme, 'utf-8')}"

# Convert URL to byte array, encoded in NFC NDEF format
def encode_ndef_uri(uri):
    uri_bytes = uri.encode('utf-8')
    ndef_message = [0x04] + list(uri_bytes)
    return ndef_message

# Binary data to be inserted
binary_data_hex = (
    "54 0F 1B 61 6E 64 72 6F 69 64 2E 63 6F 6D 3A 70 6B 67 63 6F 6D 2E 65 67 2E "
    "61 6E 64 72 6F 69 64 2E 41 6C 69 70 61 79 47 70 68 6F 6E 65 FE"
)
binary_data = [int(byte, 16) for byte in binary_data_hex.split()]

# Combine NDEF message and binary data
ndef_message = encode_ndef_uri(url) + binary_data

# Divide data into pages of 4 bytes each
pages = {}
page_number = 6  # Start from Page 6
for i in range(0, len(ndef_message), 4):
    page_data = ndef_message[i:i + 4]
    while len(page_data) < 4:
        page_data.append(0x00)
    page_hex = ' '.join(f"{byte:02X}" for byte in page_data)
    pages[f"Page {page_number}"] = page_hex
    page_number += 1

# Combine all page data
all_pages = {}
for page in range(0, 6):
    key = f"Page {page}"
    all_pages[key] = fixed_pages.get(key, '00 00 00 00')
all_pages.update(pages)
for page in range(130, 135):
    key = f"Page {page}"
    all_pages[key] = fixed_pages.get(key, '00 00 00 00')

# Generate final data file content
def generate_data_file():
    lines = [
        "Filetype: Flipper NFC device",
        "Version: 4",
        "# Device type can be ISO14443-3A, ISO14443-3B, ISO14443-4A, ISO14443-4B, ISO15693-3, FeliCa, NTAG/Ultralight, Mifare Classic, Mifare Plus, Mifare DESFire, SLIX, ST25TB, EMV",
        "Device type: NTAG/Ultralight",
        "# UID is common for all formats",
        "UID: 1D 6E 74 9A 95 00 00",
        "# ISO14443-3A specific data",
        "ATQA: 00 44",
        "SAK: 00",
        "# NTAG/Ultralight specific data",
        "Data format version: 2",
        "NTAG/Ultralight type: NTAG215",
        "Signature: 1D 6E 74 8F 9A 95 00 00 1D 6E 74 8F 9A 95 00 00 1D 6E 74 8F 9A 95 00 00 1D 6E 74 8F 9A 95 00 00",
        "Mifare version: 00 04 04 02 01 00 11 03",
        "Counter 0: 0",
        "Tearing 0: 00",
        "Counter 1: 0",
        "Tearing 1: 00",
        "Counter 2: 0",
        "Tearing 2: 00",
        "Pages total: 135",
        "Pages read: 133",
        "Failed authentication attempts: 0"
    ]
    for page_num in range(0, 135):
        key = f"Page {page_num}"
        page_data = all_pages.get(key, '00 00 00 00')
        lines.append(f"{key}: {page_data}")
    return '\n'.join(lines)

# Write data to file
with open('Alipay-nfcPay.flipper0.nfc', 'w', encoding='utf-8') as f:
    data_file_content = generate_data_file()
    f.write(data_file_content)
    print("数据文件已生成：Alipay-nfcPay.flipper0.nfc")

# Print generated page data for verification
print("\n生成的部分页面数据：")
for page_num in range(6, 10):
    key = f"Page {page_num}"
    print(f"{key}: {all_pages.get(key)}")
