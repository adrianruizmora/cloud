varsEnv=$(az keyvault secret show --name "cloudVars" --vault-name "cloudKeyVaultSimplon" --query "value")
varsEnv=${varsEnv//\"/}
varsEnv=${varsEnv//\'/}
IFS=', '
read -r -a varsEnv <<< "$varsEnv"

echo "chmod +x ./env.sh" > ./launch.sh
echo "./env.sh" >> ./launch.sh

echo >> launch.sh
for varEnv in "${varsEnv[@]}"
do  
    echo "export $varEnv" >> launch.sh
done

echo >> launch.sh
echo FLASK_APP=app >> launch.sh
echo set FLASK_DEBUG=1 >> launch.sh
echo flask run --host=0.0.0.0 --port=80 >> launch.sh
