# Trading Strategy & Backtest Framework

Outil d'analyse quantitative et de backtest de stratégies de trading développé en Python.

## 📊 Fonctionnalités du Projet

### 1. Analyse de l'Univers d'Actifs
- Téléchargement automatisé de 5 ans d'historique pour 15 actifs (actions internationales, ETF, indices, actifs ESG, taux sans risque) via `yfinance`.
- Conversion robuste des devises étrangères (USD, CNY, GBP, JPY) vers l'EUR.
- Nettoyage des données et calcul des rendements logarithmiques.
- Calcul des métriques de risque avancées : 
  - Volatilité annualisée ($\sigma_{ann} = \sigma_{quot} \times \sqrt{252}$)
  - Value at Risk (VaR) et Conditional VaR (CVaR) paramétriques à 95% et 99%
  - Drawdown maximum et temps de récupération
- Visualisations graphiques : prix normalisés base 100, heatmap des corrélations, plan rendement/risque et distributions de rendements.

### 2. Stratégies de Trading & Moteur de Backtest
- **Stratégie 1 :** Croisement de Moyennes Mobiles (courte/longue).
- **Stratégie 2 :** Indicateur Ichimoku (Tenkan-Sen / Kijun-Sen).
- **Moteur de Backtest :** Suivi dynamique des positions, du cash, de la valeur totale du portefeuille et calcul des rendements journaliers.
- **Optimisation :** Sélection des hyperparamètres optimaux basée sur le ratio de Sharpe.
- **Reporting :** Export automatique des résultats de backtest et de la synthèse globale dans un classeur Excel enrichi (`Rapport_Financier_Analyse.xlsx`).

---

## 🛠️ Installation et Utilisation

1. **Cloner le dépôt :**
   ```bash
   git clone [https://github.com/votre-nom-d-utilisateur/trading-strategy-backtest.git](https://github.com/votre-nom-d-utilisateur/trading-strategy-backtest.git)
   cd trading-strategy-backtest
2. **Installer les dépendances :**
  ```bash
  pip install -r requirements.txt
3. **Exécuter le script principal :**
  ```bash
  python Projet.py
