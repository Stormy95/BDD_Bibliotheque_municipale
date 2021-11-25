# Bilbiothèque en ligne Guide d'installation

# Ce readme sert au déploiement en ligne de l'application à partir de votre machine. 

L'application étant déjà en ligne vous n'avez pas besoin de réaliser tout cela vous pouvez directement vous connecter sur la bibliotheque avec le lien et les mots de passe par défaut suivant :
 - lien: https://stormy-gorge-70262.herokuapp.com/library_app/
 - email: default_user@ecl.com
 - mot de passe: motdepasse

## 1/ Création d'un repository sur github 

 - créer un compte github
 - Selectionner "new repository"
   - Entrer un nom de repository
   - Entrer une description
   - Cliquer sur "Create repository"
   - Ne créez pas de read.me, .gitignore, LICENCE vous utiliserez directement ceux de ce fichier 
 - Cliquer sur le bouton vert "code" et copier le lien qui apparait (ex: https://github.com/<your_git_user_id>/<your_repo_name>.git
 - Installer git sur votre ordinateur : https://git-scm.com/downloads
 - Ouvrir le terminal de commande de votre ordinateur et cloner votre repository: **git clone https://github.com/<your_git_user_id>/<your_repo_name>.git**
 - Naviguer dans le dossier créer: cd your_repo_name
   - Copier coller tout le dossier extrait de l'application dans le dossier créé
 - Ouvrir le terminal de commande de votre ordinateur et ajouter dans git le dossier copié collé: **git add -A**
 - Si vous avez bien tout copié collé utiliser les commandes suivantes pour valider et synchroniser votre repository local et sur github: 
   - **git commit -m**
   - **git push origin main**
   
## 2/ Créer un compte Heroku

 - Aller sur www.heroku.com et cliquer sur SIGN UP FOR FREE
 - Entrer vos détails et cliquer CREATE FREE ACCOUNT
 - Cliquer sur le lien d'activation dans le mail d'inscription
 - Entrer votre mot de passe et cliquer SET PASSWORD AND LOGIN 
 - Vous serez connecté et amené sur la page suivante: https://dashboard.heroku.com/apps

## 3/ Installation du client

 - Télécharger et installer le client Heroku en suivant les instructions ici: https://devcenter.heroku.com/articles/getting-started-with-python#set-up
 - Après que le client est installé vous pourrez utiliser les commandes, faites le test en écrivant sur le terminal de commande avec: **heroku help** 
 
## 4/ Créer et téléverser l'application

 - Pour créer l'app utiliser la commande suivante en ouvrant le termninal de commande au niveau du repository local: **heroku create**
 - On peut maintenant téléverser l'application et démarrer le site avec la commande suivante: **git push heroku main**
 - utiliser ensuite les commmandes suivantes pour créer la base de donnée ainsi que les tables dans cette base de donnée: 
     - **heroku run python manage.py makemigrations sessions**
     - **heroku run python manage.py migrate sessions**
 - Afin d'utiliser proprement la bilbiothèque créez vous un compte superuser avant d'aller sur le site avec la commande suivante :
     - **heroku run python manage.py createsuperuser**
     - Pour les informations par défaut pour votre première connexion nous vous suggérons les infos suivantes:
       - email adress : user@ecl.com
       - fisrt name : user_name
       - last name : user_last_name
       - social status : ET
       - password : Motdepasse1
       - password (again) : Motdepasse1
 - Vous pouvez maintenant aller directement sur le site avec la commande suivante et vous connecter avec le compte créé à l'instant: **heroku open**


