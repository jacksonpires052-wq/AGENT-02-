P=fernandabrandao-ab276; SITE=kaleuleandro; EMAIL=belliandrosolucoesimobiliarias@gmail.com
read ID KEY < ~/fbcfg.txt
T=$(gcloud auth print-access-token); A=(-H "Authorization: Bearer $T" -H "Content-Type: application/json" -H "x-goog-user-project: $P")
echo "5) Regras"; mkdir -p ~/regras && cd ~/regras && curl -sL https://raw.githubusercontent.com/jacksonpires052-wq/AGENT-02-/site-jackson-imagens/firestore.rules -o firestore.rules && echo '{"firestore":{"rules":"firestore.rules"}}' > firebase.json && firebase deploy --only firestore:rules --project $P --non-interactive 2>&1 | grep -E "Deploy complete|Error|released"
echo "6) Usuario"
PW=$(python3 -c "import secrets;print(secrets.token_urlsafe(18))")
UID_=$(curl -s -X POST "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=$KEY" -H "Content-Type: application/json" -d '{"email":"'$EMAIL'","password":"'$PW'"}' | python3 -c "import sys,json;print(json.load(sys.stdin).get('localId',''))")
[ -z "$UID_" ] && UID_=$(curl -s -X POST "${A[@]}" "https://identitytoolkit.googleapis.com/v1/projects/$P/accounts:lookup" -d '{"email":["'$EMAIL'"]}' | python3 -c "import sys,json;print(json.load(sys.stdin)['users'][0]['localId'])")
echo "uid=${UID_:0:6}..."
curl -s -X PATCH "${A[@]}" "https://firestore.googleapis.com/v1/projects/$P/databases/(default)/documents/admins/$UID_" -d '{"fields":{"site":{"stringValue":"'$SITE'"}}}' | grep -o '"site"' | head -1
echo "7) Site + painel"
cd ~/sj2 && rm -rf AGENT-02-* && curl -sL https://codeload.github.com/jacksonpires052-wq/AGENT-02-/tar.gz/site-jackson-imagens | tar xz && D=~/sj2/$(ls -d AGENT-02-* | head -1)
mkdir -p ~/site-kaleu/public/painel && cp $D/deploy-kaleu/index.html $D/deploy-kaleu/imoveis.json ~/site-kaleu/public/ && cp $D/deploy-kaleu/painel/index.html ~/site-kaleu/public/painel/
sed -i "s/__FBKEY__/$KEY/g; s/__APPID__/$ID/g" ~/site-kaleu/public/index.html ~/site-kaleu/public/painel/index.html
grep -c "__FBKEY__\|__APPID__" ~/site-kaleu/public/index.html ~/site-kaleu/public/painel/index.html
(cd ~/site-kaleu && firebase deploy --only hosting --project $P --non-interactive 2>&1 | grep -E "Hosting URL|Error")
echo "8) E-mail para criar a senha"
curl -s -X POST "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key=$KEY" -H "Content-Type: application/json" -d '{"requestType":"PASSWORD_RESET","email":"'$EMAIL'"}' | grep -o '"email"\|"message": "[^"]*"'
echo FIM
