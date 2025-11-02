from OpenSSL import crypto

# gera chave RSA 2048 e certificado autoassinado (1 ano)
key = crypto.PKey()
key.generate_key(crypto.TYPE_RSA, 2048)

cert = crypto.X509()
subj = cert.get_subject()
subj.C = "BR"
subj.ST = "SP"
subj.L = "SP"
subj.O = "LocalTest"
subj.CN = "localhost"

cert.set_serial_number(1)
cert.gmtime_adj_notBefore(0)
cert.gmtime_adj_notAfter(365*24*60*60)
cert.set_issuer(subj)
cert.set_pubkey(key)
cert.sign(key, "sha256")

with open("cert.pem", "wb") as f:
    f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
with open("key.pem", "wb") as f:
    f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

print("OK: cert.pem e key.pem gerados.")
