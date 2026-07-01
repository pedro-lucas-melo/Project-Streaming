"""
Re-sign a Tizen .wgt using RSA-SHA256 instead of RSA-SHA512.
Usage: python resign_wgt.py <input.wgt> <output.wgt>
"""
import sys, os, zipfile, hashlib, base64, shutil
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates

AUTHOR_P12  = r"C:\Users\PedroMelo\SamsungCertificate\PedroStreaming\author.p12"
DIST_P12    = r"C:\Users\PedroMelo\SamsungCertificate\PedroStreaming\distributor.p12"
AUTHOR_PWD  = b"Pedro123@"
DIST_PWD    = b"Pedro123@"

def read_pwd(path):
    return DIST_PWD

def load_p12(p12_path, pwd):
    with open(p12_path, "rb") as f:
        data = f.read()
    return load_key_and_certificates(data, pwd, default_backend())

def sha256_b64(data: bytes) -> str:
    return base64.b64encode(hashlib.sha256(data).digest()).decode()

def cert_der_b64(cert) -> str:
    return base64.b64encode(cert.public_bytes(serialization.Encoding.DER)).decode()

def sign_bytes(key, data: bytes) -> str:
    sig = key.sign(data, padding.PKCS1v15(), hashes.SHA256())
    return base64.b64encode(sig).decode()

def make_reference_xml(uri, digest_b64):
    return (
        f'<Reference URI="{uri}">'
        f'<DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"></DigestMethod>'
        f'<DigestValue>{digest_b64}</DigestValue>'
        f'</Reference>'
    )

def make_reference_with_transform(uri, digest_b64):
    return (
        f'<Reference URI="{uri}">'
        f'<Transforms><Transform Algorithm="http://www.w3.org/2006/12/xml-c14n11"></Transform></Transforms>'
        f'<DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"></DigestMethod>'
        f'<DigestValue>{digest_b64}</DigestValue>'
        f'</Reference>'
    )

def prop_xml(sig_id):
    return (
        f'<Object xmlns="http://www.w3.org/2000/09/xmldsig#" Id="prop">'
        f'<SignatureProperties xmlns:dsp="http://www.w3.org/2009/xmldsig-properties">'
        f'<SignatureProperty Id="profile" Target="#{sig_id}">'
        f'<dsp:Profile URI="http://www.w3.org/ns/widgets-digsig#profile"></dsp:Profile>'
        f'</SignatureProperty>'
        f'<SignatureProperty Id="role" Target="#{sig_id}">'
        f'<dsp:Role URI="http://www.w3.org/ns/widgets-digsig#role-distributor"></dsp:Role>'
        f'</SignatureProperty>'
        f'<SignatureProperty Id="identifier" Target="#{sig_id}">'
        f'<dsp:Identifier></dsp:Identifier>'
        f'</SignatureProperty>'
        f'</SignatureProperties>'
        f'</Object>'
    )

def author_prop_xml(sig_id):
    return (
        f'<Object xmlns="http://www.w3.org/2000/09/xmldsig#" Id="prop">'
        f'<SignatureProperties xmlns:dsp="http://www.w3.org/2009/xmldsig-properties">'
        f'<SignatureProperty Id="profile" Target="#{sig_id}">'
        f'<dsp:Profile URI="http://www.w3.org/ns/widgets-digsig#profile"></dsp:Profile>'
        f'</SignatureProperty>'
        f'<SignatureProperty Id="role" Target="#{sig_id}">'
        f'<dsp:Role URI="http://www.w3.org/ns/widgets-digsig#role-author"></dsp:Role>'
        f'</SignatureProperty>'
        f'<SignatureProperty Id="identifier" Target="#{sig_id}">'
        f'<dsp:Identifier></dsp:Identifier>'
        f'</SignatureProperty>'
        f'</SignatureProperties>'
        f'</Object>'
    )

def build_signed_info(references_xml, canon_method="http://www.w3.org/2001/10/xml-exc-c14n#"):
    return (
        f'<SignedInfo xmlns="http://www.w3.org/2000/09/xmldsig#">'
        f'<CanonicalizationMethod Algorithm="{canon_method}"></CanonicalizationMethod>'
        f'<SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"></SignatureMethod>'
        f'{references_xml}'
        f'</SignedInfo>'
    )

def build_signature_xml(sig_id, signed_info, sig_value, key_info_certs, prop_obj):
    certs_xml = "".join(
        f"<X509Certificate>{c}</X509Certificate>" for c in key_info_certs
    )
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<Signature xmlns="http://www.w3.org/2000/09/xmldsig#" Id="{sig_id}">'
        f'{signed_info}'
        f'<SignatureValue>{sig_value}</SignatureValue>'
        f'<KeyInfo><X509Data>{certs_xml}</X509Data></KeyInfo>'
        f'{prop_obj}'
        f'</Signature>'
    )

def resign(input_wgt, output_wgt):
    # Load certs
    dist_pwd = read_pwd(DIST_P12.replace(".p12", ".pwd"))
    auth_key, auth_cert, auth_chain = load_p12(AUTHOR_P12, AUTHOR_PWD)
    dist_key, dist_cert, dist_chain = load_p12(DIST_P12, dist_pwd)

    # Extract wgt
    tmp_dir = Path(input_wgt).with_suffix(".tmp_resign")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir()

    with zipfile.ZipFile(input_wgt, "r") as z:
        z.extractall(tmp_dir)

    # Remove old signatures
    for f in ["author-signature.xml", "signature1.xml"]:
        p = tmp_dir / f
        if p.exists():
            p.unlink()

    # Collect content files (exclude signatures)
    sig_files = {"author-signature.xml", "signature1.xml"}
    content_files = sorted(
        p.name for p in tmp_dir.iterdir()
        if p.is_file() and p.name not in sig_files
    )

    # --- Author signature ---
    auth_refs = ""
    for name in content_files:
        data = (tmp_dir / name).read_bytes()
        auth_refs += make_reference_xml(name, sha256_b64(data))

    # prop digest
    auth_prop = author_prop_xml("AuthorSignature")
    prop_bytes = auth_prop.encode("utf-8")
    auth_refs += make_reference_with_transform("#prop", sha256_b64(prop_bytes))

    auth_signed_info = build_signed_info(auth_refs)
    auth_sig_value = sign_bytes(auth_key, auth_signed_info.encode("utf-8"))

    auth_certs = [cert_der_b64(auth_cert)]
    if auth_chain:
        for c in auth_chain:
            auth_certs.append(cert_der_b64(c))

    auth_xml = build_signature_xml(
        "AuthorSignature", auth_signed_info, auth_sig_value,
        auth_certs, auth_prop
    )
    (tmp_dir / "author-signature.xml").write_text(auth_xml, encoding="utf-8")

    # --- Distributor signature (signature1.xml) ---
    # includes content files + author-signature.xml
    dist_content = content_files + ["author-signature.xml"]
    dist_refs = ""
    for name in sorted(dist_content):
        data = (tmp_dir / name).read_bytes()
        dist_refs += make_reference_xml(name, sha256_b64(data))

    dist_prop = prop_xml("DistributorSignature")
    prop_bytes2 = dist_prop.encode("utf-8")
    dist_refs += make_reference_with_transform("#prop", sha256_b64(prop_bytes2))

    dist_signed_info = build_signed_info(dist_refs)
    dist_sig_value = sign_bytes(dist_key, dist_signed_info.encode("utf-8"))

    dist_certs = [cert_der_b64(dist_cert)]
    if dist_chain:
        for c in dist_chain:
            dist_certs.append(cert_der_b64(c))

    dist_xml = build_signature_xml(
        "DistributorSignature", dist_signed_info, dist_sig_value,
        dist_certs, dist_prop
    )
    (tmp_dir / "signature1.xml").write_text(dist_xml, encoding="utf-8")

    # Repack
    out = Path(output_wgt)
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(tmp_dir.iterdir()):
            z.write(f, f.name)

    shutil.rmtree(tmp_dir)
    print(f"Done: {output_wgt}")
    print(f"Files signed: {sorted(dist_content)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python resign_wgt.py <input.wgt> <output.wgt>")
        sys.exit(1)
    resign(sys.argv[1], sys.argv[2])
