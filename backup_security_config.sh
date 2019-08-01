#!/usr/bin/env bash

docker exec -it $(docker ps -aqf "name=odfe-node") bash -c "cd /usr/share/elasticsearch/plugins/opendistro_security && tools/securityadmin.sh  -backup ~/security_config -icl -nhnv -cacert ../../config/root-ca.pem -cert ../../config/admin.pem -key ../../config/admin-key.pem && tar -zcvf ~/security_config.tar.gz -C ~/security_config . && rm -rf ~/security_config"
docker cp $(docker ps -aqf "name=odfe-node"):/root/security_config.tar.gz ~/security_config
docker exec -it $(docker ps -aqf "name=odfe-node") bash -c "rm ~/security_config.tar.gz"
aws s3 cp ~/security_config/security_config.tar.gz s3://$ES_SNAPSHOT_BUCKET/security_config/`date +%y-%m`/security_config-`date +%y-%m-%d-%H`.tar.gz
