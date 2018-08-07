import sys
import hashlib
import time
import base64

def sha_and_md5(file_name):
	BUF_SIZE = 65536

	md5 = hashlib.md5()
	sha512 = hashlib.sha512()

	with open(file_name, 'rb') as f:
		while True:
			data = f.read(BUF_SIZE)
			if not data:
				break
			md5.update(data)
			sha512.update(data)

	return md5.hexdigest(), sha512.hexdigest(), base64.b64encode(md5.digest()).decode('utf-8')

if __name__ == "__main__":

	file_to_process = str(sys.argv[1])

	scene_md5, scene_sha, scene_md5_base64 = sha_and_md5(file_to_process)

	print("MD5 of File: ", scene_md5)
	print("SHA-512 of file: ", scene_sha)
	print("SHA-512 Base 64 of file: ", scene_md5_base64)