P=fernandabrandao-ab276; SITE=kaleuleandro; EMAIL=belliandrosolucoesimobiliarias@gmail.com
T=$(gcloud auth print-access-token); A=(-H "Authorization: Bearer $T" -H "Content-Type: application/json" -H "x-goog-user-project: $P")
echo "1) APIs"; gcloud services enable firestore.googleapis.com identitytoolkit.googleapis.com --project $P 2>&1 | tail -1
echo "2) Firestore"; gcloud firestore databases create --location=southamerica-east1 --project $P 2>&1 | grep -iE "created|already|error" | head -2
echo "3) Login por e-mail"
DOMS='"localhost","'$P'.firebaseapp.com","'$P'.web.app","kaleuleandro.web.app","imobiliariabelliandro.com.br","www.imobiliariabelliandro.com.br","jacksonpires.web.app","douglasconceicao.web.app"'
R=$(curl -s -X PATCH "${A[@]}" "https://identitytoolkit.googleapis.com/admin/v2/projects/$P/config?updateMask=signIn.email.enabled,signIn.email.passwordRequired,authorizedDomains" -d '{"signIn":{"email":{"enabled":true,"passwordRequired":true}},"authorizedDomains":['"$DOMS"']}')
echo "$R" | python3 -c "import sys,json;j=json.load(sys.stdin);print('ERRO',j['error']['message']) if 'error' in j else print('ok, email', j.get('signIn',{}).get('email'))"
echo "4) App web"
ID=$(firebase apps:list WEB --project $P --json 2>/dev/null | python3 -c "import sys,json;r=json.load(sys.stdin).get('result',[]);print(r[0]['appId'] if r else '')")
[ -z "$ID" ] && ID=$(firebase apps:create WEB "Paineis" --project $P --json 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin)['result']['appId'])")
KEY=$(firebase apps:sdkconfig WEB $ID --project $P --json 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin)['result']['sdkConfig']['apiKey'])")
echo "app=$ID key=${KEY:0:8}..."; echo "$ID $KEY" > ~/fbcfg.txt
