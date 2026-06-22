# Calculator API - Python Implementation

Une API REST simple de calculatrice implémentée en **Python** avec **FastAPI** et **Uvicorn**. Ce projet est la traduction Python de [calculator-api-js](https://github.com/Loocist23/calculator-api-js), une API Node.js originale.

## 📁 Structure du projet

```
calculator-api-python/
├── src/
│   ├── __init__.py
│   ├── calculator.py      # Logique métier (Calculator class)
│   └── main.py            # Serveur FastAPI
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # Configuration pytest
│   ├── helpers/
│   │   └── __init__.py
│   │   └── http.py        # Helper HTTP pour les tests
│   ├── test_calculator.py # Tests unitaires pour Calculator
│   ├── test_api.py        # Tests d'intégration pour l'API
│   └── test_injection.py  # Tests de sécurité - Injection
├── .gitignore
├── pyproject.toml          # Configuration du projet
├── README.md               # Documentation
└── requirements.txt        # Dépendances
```

## 🚀 Installation

```bash
# Cloner le dépôt (ou naviguer jusqu'au dossier)
cd calculator-api-python

# Créer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate  # Sur Linux/Mac
# .\.venv\Scripts\activate  # Sur Windows

# Installer les dépendances
pip install -r requirements.txt

# Pour le développement, installer aussi les dépendances dev
pip install -e ".[dev]"
```

## 📋 Scripts disponibles

| Commande | Description |
|----------|-------------|
| `uvicorn src.main:app --reload` | Démarre le serveur avec rechargement automatique |
| `python -m pytest` | Exécute tous les tests (unitaires + intégration + sécurité) |
| `python -m pytest tests/test_calculator.py` | Exécute uniquement les tests unitaires |
| `python -m pytest tests/test_api.py` | Exécute uniquement les tests d'intégration |
| `python -m pytest tests/test_injection.py` | Exécute uniquement les tests de sécurité |
| `python -m pytest --cov=src` | Exécute les tests avec couverture de code |
| `black src tests` | Formate le code avec Black |
| `flake8 src tests` | Vérifie la qualité du code avec Flake8 |

## 🧪 Tests

### Tests unitaires (30+ tests)

Les tests unitaires couvrent la classe `Calculator` en isolation :

- **add(a, b)** : Addition de deux nombres
  - Nombres positifs, négatifs, zéro
  - Nombres décimaux (avec `pytest.approx`)
  - Problèmes de précision flottante (0.1 + 0.2)

- **subtract(a, b)** : Soustraction de deux nombres
  - Tous les cas de base
  - Précision flottante

- **multiply(a, b)** : Multiplication de deux nombres
  - Nombres positifs et négatifs
  - Multiplication par zéro
  - NaN propagation

- **divide(a, b)** : Division de deux nombres
  - Division normale
  - **Division par zéro** : Lève une ValueError avec le message exact `"Division par zéro impossible."`
  - Comportement avec NaN

### Tests d'intégration (30+ tests)

Les tests d'intégration testent l'API comme un client externe avec de vraies requêtes HTTP :

- **Performance** : Temps de réponse < 100ms
- **Headers** : Vérification des headers CORS et Content-Type
- **OPTIONS** : Preflight CORS (status 204)
- **Cas nominaux** : Toutes les opérations avec différents paramètres
- **Méthodes non autorisées** : POST, PUT, DELETE → 405
- **Erreurs 400** : Paramètres manquants, non numériques, division par zéro, opération inconnue
- **Autres routes** : 404 pour les routes inconnues
- **Edge cases** : Très grandes valeurs, -0, encodage URL, etc.

### Tests de sécurité (100+ tests)

Les tests de sécurité vérifient la résistance de l'API aux attaques par injection :

- **Injection JavaScript** : Code JS, template literals
- **Injection SQL** : DROP TABLE, UNION SELECT, commentaires
- **XSS** : Balises script, img, onerror, javascript: URL
- **Injection de commandes** : |, ;, &&, backticks, $()
- **Prototype Pollution** : __proto__, constructor.prototype
- **Path Traversal** : ../etc/passwd, null bytes
- **Regex Injection** : /pattern/, .*, etc.
- **Format String Attacks** : %s, %n
- **HTTP Parameter Pollution** : Paramètres dupliqués
- **Attaques par strings longs** : DoS avec 10000 caractères
- **Caractères Unicode malveillants** : Zero-width spaces, caractères de contrôle
- **Encodages malveillants** : Double encoding, etc.

### Exécution des tests

```bash
# Tous les tests
python -m pytest

# Avec couverture de code
python -m pytest --cov=src --cov-report=html

# Voir le rapport de couverture
open htmlcov/index.html
```

## 🌐 API Endpoint

### GET /calculate

**Requête :**
```
GET /calculate?operation=<op>&a=<nombre>&b=<nombre>
```

**Paramètres requis :**
- `operation` (string) : Une des opérations : `add`, `subtract`, `multiply`, `divide`
- `a` (number) : Premier opérande
- `b` (number) : Deuxième opérande

**Réponse réussie (200) :**
```json
{
  "operation": "add",
  "a": 5.0,
  "b": 3.0,
  "result": 8.0
}
```

**Réponse erreur (400) :**
```json
{
  "detail": "Division par zéro impossible."
}
```

### Codes HTTP et messages d'erreur

| Code | Situation | Message d'erreur |
|------|-----------|-----------------|
| 200 | Calcul réussi | - |
| 400 | Opération inconnue | `"Opération inconnue. Utiliser : add, subtract, multiply, divide"` |
| 400 | Division par zéro | `"Division par zéro impossible."` |
| 404 | Route introuvable | `"Route introuvable."` |
| 404 | Paramètre manquant | FastAPI retourne 404 pour les paramètres requis manquants |
| 422 | Paramètre non numérique | FastAPI retourne 422 pour les types invalides |
| 405 | Méthode non autorisée | `"Méthode non autorisée. Utiliser GET."` |
| 204 | OPTIONS (preflight CORS) | - (body vide) |

### Headers CORS

Toutes les réponses incluent les headers CORS :
```
Content-Type: application/json
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

## 📊 Couverture de code

Avec pytest-cov, vous pouvez générer un rapport de couverture :

```bash
python -m pytest --cov=src --cov-report=html
```

## 🔧 Différences avec l'API Node.js originale

### Frameworks
- **Original** : Node.js avec modules natifs `http` et `url`
- **Python** : FastAPI avec Uvicorn (ASGI)

### Gestion des erreurs
- **Original** : Codes HTTP 400 pour la plupart des erreurs de validation
- **Python** : 
  - FastAPI retourne **422** pour les erreurs de validation de type (paramètres non numériques)
  - Retourne **404** pour les paramètres requis manquants
  - Retourne **400** pour les erreurs logiques (division par zéro, opération inconnue)

### Comportement de coercion de types
- **JavaScript** : Coercion automatique (null → 0, "5" + "3" → "53")
- **Python** : Pas de coercion automatique, FastAPI valide les types strictement
  - Les paramètres sont définis comme `float`, donc FastAPI rejette les non-nombres avec 422
  - Pour répliquer le comportement JS, il faudrait accepter des strings et faire la conversion manuellement

### Performances
- FastAPI est généralement **beaucoup plus rapide** que le serveur HTTP natif de Node.js
- Les tests de performance (< 100ms) passent facilement

## 💡 Points clés implémentés

### 1. Logique métier (src/calculator.py)

- **Classe Calculator** avec 4 méthodes : `add`, `subtract`, `multiply`, `divide`
- **Gestion des erreurs** : `divide(a, 0)` lève `ValueError("Division par zéro impossible.")`
- **Documentation complète** avec docstrings

### 2. Serveur API (src/main.py)

- **FastAPI** avec Uvicorn (ASGI)
- **Routing** : `/calculate` avec méthode GET
- **Validation** via les annotations de type et Query de FastAPI
- **CORS** : Configuré avec CORSMiddleware
- **Gestion des erreurs** personnalisée pour la division par zéro
- **OPTIONS** : Support complet pour le preflight CORS

### 3. Tests complets

- **160+ tests** : Tests unitaires, d'intégration et de sécurité
- **pytest** : Framework de test moderne
- **pytest-cov** : Couverture de code
- **TestClient** : Client de test FastAPI pour les tests d'intégration
- **Fixtures** : Configuration centralisée dans conftest.py

### 4. Sécurité

L'API est protégée contre :
- Injection SQL
- XSS (Cross-Site Scripting)
- Injection de commandes
- Prototype Pollution
- Path Traversal
- Regex Injection
- Format String Attacks
- HTTP Parameter Pollution
- Attaques par strings longs (DoS)
- Caractères Unicode malveillants

## 📝 Documentation des comportements

### Comportement Python vs JavaScript

| Appel | Résultat (JavaScript) | Résultat (Python) | Explication |
|-------|----------------------|-------------------|-------------|
| `add(null, 2)` | `2` | `TypeError` | JS coerce null en 0, Python non |
| `add(undefined, 5)` | `NaN` | `TypeError` | JS coerce undefined en NaN, Python lève une erreur |
| `multiply("abc", 3)` | `NaN` | `TypeError` | JS coerce, Python non |
| `add("5", "3")` | `"53"` | `"53"` | Concaténation dans les deux cas |
| `divide(NaN, 5)` | `NaN` | `NaN` | Comportement similaire |

## 🎯 Objectifs pédagogiques atteints

✅ Implémentation d'une API REST avec FastAPI (équivalent moderne d'Express/Koa)
✅ Logique métier isolée et testable
✅ Tests unitaires complets avec pytest
✅ Tests d'intégration avec TestClient
✅ Tests de sécurité exhaustifs
✅ Gestion des erreurs (division par zéro, opérations inconnues)
✅ Configuration CORS complète
✅ Couverture de code avec pytest-cov
✅ Documentation complète en français
✅ Intégration continue prête (GitHub Actions compatible)

## 🔗 Liens

- **Dépôt GitHub original (Node.js)** : [https://github.com/Loocist23/calculator-api-js](https://github.com/Loocist23/calculator-api-js)
- **FastAPI** : [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **Pytest** : [https://docs.pytest.org/](https://docs.pytest.org/)

## 📜 Licence

ISC
