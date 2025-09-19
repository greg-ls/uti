## développement
Visual Studio Code en local + Visual Studio Code Server sur le serveur (port 9090/login)

## client
Termius pour l'interface ligne de commande + ftp secondaire (https://termius.com/)
FileZilla en client ftp

## serveur

### outils
ftp pour fileZilla
tmux pour mettre l'application en tâche de fond et pouvoir fermer la session sans tuer l'application
lsfo pour lister les processus sur un port spécifique.
gunicorn pour serveur de prod sur port 5000
flask pour serveur de test sur autre port
python 3.12.9 avec un gestionnaire d'environnement (micromamba pour ce projet)
pdftotext pour la conversion des pdf++ (sudo apt install poppler-utils)

### lancer l'application:
se positionner dans /home/steeve/cv_format
<commande>tmux</commande>
<commande>gunicorn -w 6 -b 0.0.0.0:5000 --timeout 600 app:app</commande>
>> -w 6 pour instancier 6 workers
>> -b 0.0.0.0:5000 pour lier l'application au port 5000
>> --timeout 600 annonce que l'on donne 10 minute au worker pour réaliser sa tâche
>> app:app relation entre app.py et la ligne app = Flask(__name__)
CTRL+B puis D pour sortir de tmux

<commande>tmux attach</commande>
pour repasser dans la fenêtre tâche de fond.

### relancer l'application:
Si besoin de maintenance
<commande>lsof -i :5000</commande>
pour lister les process qui sont liés au port 5000 puis
<commande>kill -9 PROCESS_ID</commande>
pour tuer les workers avant de relancer l'application.
