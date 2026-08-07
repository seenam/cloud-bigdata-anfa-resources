# Fiche de conformité — Application mobile passagers Anfa

> Gabarit fourni. Complétez chaque section **en 2-4 lignes**, en vous appuyant sur le CM.
> Il n'y a pas de "bonne réponse" unique sur certains points — l'important est le raisonnement.

## 1. Finalité du traitement
La collecte vise trois usages précis et limités : la position GPS sert uniquement à proposer le trajet/arrêt le plus proche en temps réel, l'historique de paiement mobile money sert à gérer l'abonnement (facturation, renouvellement), et le numéro de téléphone sert d'identifiant de compte. Aucune de ces données ne doit être réutilisée pour un usage secondaire (profilage publicitaire, revente à des tiers, scoring commercial) sans nouvelle base légale et information claire du passager.

## 2. Données collectées et leur sensibilité
Les trois données sont : la position GPS, l'historique de paiements mobile money, le numéro de téléphone. La position GPS est la plus sensible : collectée en continu, elle permet de reconstituer les déplacements d'une personne (domicile, travail, habitudes), ce qui est intrusif même sans autre donnée associée. L'historique de paiement est également sensible car il révèle des informations financières (montants, fréquence, niveau de vie) ; le numéro de téléphone est un identifiant direct mais, seul, moins révélateur que les deux autres.

## 3. Base légale applicable
La loi togolaise n°2019-014 relative à la protection des données à caractère personnel s'applique aux trois données en tant que données personnelles : elle impose consentement (ou autre base légale légitime), finalité déterminée, et déclaration/autorisation auprès de l'autorité de protection des données. L'historique de paiement mobile money relève en plus de la réglementation sur les transactions électroniques et la lutte contre le blanchiment (loi 2017-007/2023-012 et règles BCEAO/UMOA sur la monnaie électronique), qui impose ses propres obligations de traçabilité et de conservation — les deux textes se cumulent car une même donnée peut être à la fois une donnée personnelle et une donnée financière réglementée.

## 4. Durée de conservation
Par principe de minimisation, chaque donnée ne doit être gardée que le temps nécessaire à sa finalité : la position GPS ne devrait être conservée que le temps du trajet (éventuellement quelques jours pour gérer un litige), puis supprimée ou agrégée/anonymisée pour les besoins statistiques (comme le dataset d'affluence de ce TP, qui ne contient plus d'identifiant individuel). L'historique de paiement, lui, doit être conservé plus longtemps car les obligations comptables et de lutte anti-blanchiment imposent une durée minimale (plusieurs années), ce qui prime temporairement sur la minimisation stricte.

## 5. Hébergement et souveraineté
Pour rester conforme à la loi togolaise, ces données devraient être hébergées au Togo ou, à défaut, dans un pays offrant un niveau de protection reconnu équivalent, avec l'accord de l'autorité de protection des données pour tout transfert transfrontalier. Héberger chez un cloud américain expose les données au Cloud Act/Patriot Act, qui permet aux autorités américaines d'y accéder sur simple réquisition, même si le service tourne dans une région hors des États-Unis — ce qui contourne la protection légale togolaise et crée un risque juridique et de souveraineté pour Anfa.

## 6. Droit des personnes concernées
Oui, un passager doit pouvoir demander l'accès, la rectification et la suppression de ses données (droit à l'effacement), conformément à la loi 2019-014. Le système technique actuel d'Anfa (données brutes dans le stockage objet, pipelines ETL, entrepôt, modèles ML comme celui de ce TP) ne le permettrait pas facilement : les données d'une même personne sont dispersées entre plusieurs systèmes (bruts, transformés, agrégés, artefacts de modèle) sans identifiant unique traçable de bout en bout ni procédure d'effacement automatisée — un vrai chantier de gouvernance restant à construire.
