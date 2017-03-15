r"""
A module to help with encrypting and decrypting the strings.

#From: The module is improved over the script ccavutil.py from CCAvenue's integration kit for python.
"""
import md5
import pyaes

# Data
iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'

# Helpers
def pad(data):
	length = 16 - (len(data) % 16)
	data += chr(length) * length
	return data

def unpad(data):
	return data[:-ord(data[len(data)-1])]

def getAES(key):
	digest = md5.new()
	digest.update(key)

	return pyaes.AESModeOfOperationCBC(digest.digest(), iv=iv)

def spliceString(string, length=1):
	for block in [string[i:i+length] for i in range(0, len(string), length)]:
		yield block

# Exports
def encrypt(plainText, key):
	plainText = pad(plainText)
	aes = getAES(key)
	encryptedText = ''

	for block in spliceString(plainText, 16):
		encryptedText += aes.encrypt(block)

	return encryptedText.encode('hex')

def decrypt(cipherText, key):
	encryptedText = cipherText.decode('hex')
	aes = getAES(key)
	decryptedText = ''

	for block in spliceString(encryptedText, 16):
		decryptedText += aes.decrypt(block)

	return unpad(decryptedText)
