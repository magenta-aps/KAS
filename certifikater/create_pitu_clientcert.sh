openssl req -x509 -newkey rsa:4096 -keyout kas_pitu.key -out kas_pitu.crt -sha256 -days 730 -nodes -subj "/C=GL/ST=Sermersooq/L=Nuuk/O=Magenta ApS/CN=KAS Pitu Client"
echo "Oprettede kas_pitu.crt og kas_pitu.key"
echo "Gå ind i PITU -> PITU : GOV : DIA : kas -> Internal TLS Certificates -> add, og upload kas_pitu.crt"
echo "Erstat pitu_cert og pitu_key i salt pillardata secrets for KAS test og prod med indholdet af disse filer"
