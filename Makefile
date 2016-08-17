.PHONY: preview

docker_build:
	docker-compose build
	docker tag gengen_qualifier:latest polejniczak/gengen-qualifier:latest
	docker tag gengen_renderer:latest polejniczak/gengen-renderer:latest
	docker tag gengen_controller:latest polejniczak/gengen-controller:latest
	docker tag gengen_monitor:latest polejniczak/gengen-monitor:latest

docker_push:
	docker push polejniczak/gengen-qualifier:latest
	docker push polejniczak/gengen-renderer:latest
	docker push polejniczak/gengen-controller:latest
	docker push polejniczak/gengen-monitor:latest

kube_clean:
	kubectl delete deployment -l app=gengen
	kubectl delete service -l app=gengen
	kubectl delete pv -l app=gengen
	kubectl delete pvc -l app=gengen

kube_local_deploy:
	kubectl create -f kubernetes-common.yml
	kubectl create -f kubernetes-volumes.local.yml
	kubectl create -f monitor/kubernetes.yml
	kubectl create -f monitor/kubernetes.local.yml
	kubectl create -f qualifier/kubernetes.yml
	kubectl create -f renderer/kubernetes.yml
	kubectl create -f controller/kubernetes.yml
	echo http://192.168.99.100:$$(kubectl get service -l role=monitor -o jsonpath={.items[0].spec.ports[0].nodePort})

# gcloud container clusters create gengen-1 --disk-size 50 --machine-type n1-highcpu-8 --num-nodes 1 --zone europe-west1-d
# gcloud container clusters get-credentials gengen-1
# kubectl cluster-info | grep dash
# kubectl scale deployment hello-node --replicas=4
kube_gcloud_deploy:
	kubectl create -f kubernetes-common.yml
	kubectl create -f kubernetes-volumes.local.yml
	kubectl create -f monitor/kubernetes.yml
	kubectl create -f monitor/kubernetes.gcloud.yml
	kubectl create -f qualifier/kubernetes.yml
	kubectl create -f renderer/kubernetes.yml
	kubectl create -f controller/kubernetes.yml
	echo http://$$(kubectl get svc -l role=monitor -o jsonpath={.items[0].status.loadBalancer.ingress[0].ip})

kube_gcloud_clean_cluster:
	gcloud container clusters delete gengen-1

