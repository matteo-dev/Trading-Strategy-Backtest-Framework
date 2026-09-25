import yfinance as yf #Bibliotheque pour avoir acces aux donnees financieres
import pandas as pd #Bibliotheque pour la gestion de la data
import matplotlib.pyplot as plt #Bibliotheque pour la visualisation de la data
import numpy as np #Bibliotheque pour les calculs 
import seaborn as sns #Bibliotheque pour la visualisation de la data
from scipy.stats import norm #Bibliotheque pour la distribution normale

# Partie 1 – Analyse d’un univers d’actifs financiers


# Selectionner au minimum 15 actifs financiers (actions, ETF, indices,crypto) dont au minimum 5 en devise étrangère, 3 fonds (ETFs ouOPCVM), 1 fonds de type ESG, 1 indice de marché et un actif moins risqué comme le taux sans risque (^IRX ou un fonds monétaire)
tickers = [
    'MSFT',  # Action américaine Microsoft
    'GOOGL', # Action américaine Google
    'AMZN',  # Action américaine Amazon
    'TSLA',  # Action américaine Tesla
    'BABA',  # Action chinoise Alibaba
    'TCEHY', # Action chinoise Tencent
    'SAP',   # Action allemande SAP
    'BMW.DE',# Action allemande BMW
    'BNP.PA',# Action française BNP Paribas
    'VGK',   # ETF européen 
    'VWO',   # ETF marchés émergents 
    'IVV',   # ETF S&P 500 
    'ESGV',  # ETF ESG
    '^GSPC', # Indice S&P 500
    '^IRX'   # Taux sans risque américain
]

print("\n Nous avons bien telecharger les 15 actifs financiers :", tickers)

# Utiliser la librairie yfinance pour télécharger les données historiques (5 ans minimum)
data = {}
for ticker in tickers:
    df_ticker = yf.download(ticker, period='5y', auto_adjust=True)
    # Si le DataFrame a plusieurs colonnes ce qui peut arriver (Close, Open ...)alors on garde que la première donc le close
    if isinstance(df_ticker, pd.DataFrame):
        df_ticker = df_ticker.iloc[:, 0]
    data[ticker] = df_ticker

# Concatener les donnees sous un seul et meme DataFrame
df = pd.concat(data, axis=1)
df.columns = tickers

print("\n Nous avons bien telecharger les donnees historiques des actifs financiers.", df.head())

# Télécharger les taux de change nécessaires (dans ce cas européen vers autres devises)
exchange_rates = {
    'EURUSD=X': ['MSFT', 'GOOGL', 'AMZN', 'TSLA', 'IVV', 'ESGV', '^GSPC', '^IRX'], # USD vers EUR
    'EURCNY=X': ['BABA', 'TCEHY'], # CNY vers EUR
    'EURGBP=X': ['BNP.PA'], # GBP vers EUR
    'EURJPY=X': ['SAP', 'BMW.DE'], # JPY vers EUR
}

print("\n Nous avons bien telecharger les taux de change necessaires pour la conversion en EUR.", exchange_rates)

# Mettre en cache les données de prix
exchange_data = {}
# Telecharger les donners liees aux taux de change
for rate in exchange_rates.keys():
    df_rate = yf.download(rate, period='5y', auto_adjust=True)
    # Si le DataFrame a plusieurs colonnes ce qui peut arriver (Close, Open ...)alors on garde que la première donc le close
    if isinstance(df_rate, pd.DataFrame):
        df_rate = df_rate.iloc[:, 0]
    exchange_data[rate] = df_rate

print("\n Nous avons bien telecharger les donnees de prix des taux de change.", exchange_data.keys())

# convert_to_eur() : convertit les prix dans une devise étrangère en EUR selon les taux de change
def convert_to_eur(df, exchange_data, exchange_rates):
    df_eur = df.copy()
    # Boucle sur l'ensemble des taux de change et des actifs lies
    for rate, assets in exchange_rates.items():
        for asset in assets:
            # Verifie si l'actif est bien dans le dataset 
            if asset in df_eur.columns:
                df_eur[asset] = df_eur[asset] / exchange_data[rate]
    return df_eur

df_eur = convert_to_eur(df, exchange_data, exchange_rates)

print("\n Nous avons bien converti les prix des actifs financiers en EUR.", df_eur.head())

# clean_data() : gère les données manquantes, supprime les doublons, etc.
def clean_data(df):
    # Supprimer les doublons et remplir les valeurs manquantes
    df_cleaned = df.drop_duplicates()
    df_cleaned = df_cleaned.ffill().bfill()
    return df_cleaned

df_cleaned = clean_data(df_eur)

print("\n Nous avons bien nettoye les donnees des actifs financiers.", df_cleaned.head())

# calculate_returns() : calcule les rendements logarithmiques
def calculate_returns(df):
    # Calcul des rendements logarithmiques
    returns = np.log(df / df.shift(1))
    return returns.dropna()

returns = calculate_returns(df_cleaned)

print("\n Nous avons bien calcule les rendements logarithmiques des actifs financiers.", returns.head())

# calculate_performance() : calcule les performances 6M, 1Y, 3Y et 5Y (absolues et annualisées)
def calculate_performance(df):
    performance = {}
    # Choix des periode en jours de bourse (erreur approximative)
    periods = {'6M': 126, '1Y': 252, '3Y': 756, '5Y': 1260}
    for period, days in periods.items():
        # Calcul des performances absolues et annualisees
        abs_perf = (df.iloc[-1] / df.iloc[-days] - 1) * 100
        ann_perf = ((df.iloc[-1] / df.iloc[-days]) ** (252/days) - 1) * 100
        performance[period] = {'Absolute': abs_perf, 'Annualized': ann_perf}
    return performance

performance = calculate_performance(df_cleaned)

print("\n Nous avons bien calcule les performances des actifs financiers.", performance)

# Créer un DataFrame de synthèse consolidé avec l’univers d’investissement contenant : • Identifiant, nom de l’actif, devise d’origine, secteur/géographie • Performances sur différentes périodes
summary_data = []
for ticker in tickers:
    asset_info = yf.Ticker(ticker).info
    summary_data.append({
        'Ticker': ticker, # Identifiant
        'Name': asset_info.get('shortName', 'N/A'), # Nom de l'actif
        'Currency': asset_info.get('currency', 'N/A'), # Devise d'origine
        'Sector': asset_info.get('sector', 'N/A'), # Secteur
        'Geography': asset_info.get('country', 'N/A'), # Lieu de cotation
        '6M Absolute': performance['6M']['Absolute'].get(ticker, np.nan),
        '6M Annualized': performance['6M']['Annualized'].get(ticker, np.nan),
        '1Y Absolute': performance['1Y']['Absolute'].get(ticker, np.nan),
        '1Y Annualized': performance['1Y']['Annualized'].get(ticker, np.nan),
        '3Y Absolute': performance['3Y']['Absolute'].get(ticker, np.nan),
        '3Y Annualized': performance['3Y']['Annualized'].get(ticker, np.nan),
        '5Y Absolute': performance['5Y']['Absolute'].get(ticker, np.nan),
        '5Y Annualized': performance['5Y']['Annualized'].get(ticker, np.nan),
    })

summary_df = pd.DataFrame(summary_data)
print("\n DataFrame de synthese des actifs financiers :")
print(summary_df)

# Implémenter les métriques de risque

# calculate_volatility() : volatilité annualisée basée sur les log-returns
def calculate_volatility(returns):
    # Calcul de la volatilite annualisee
    volatility = returns.std() * np.sqrt(252)
    return volatility

volatility = calculate_volatility(returns)
print("Volatilite annualisee:\n", volatility)

# calculate_var_cvar() : VaR et CVaR paramétriques normales (95% et 99%, horizon 1 an)
def calculate_var_cvar(returns, confidence_levels=[0.95, 0.99]):
    var_cvar = {}
    # Calcul des deux paramètres pour chaque niveau de confiance
    for cl in confidence_levels:
        z = norm.ppf(1 - cl)
        var = returns.mean() + z * returns.std()
        cvar = returns[returns <= var].mean()
        var_cvar[cl] = {col: {'VaR': var[col], 'CVaR': cvar[col]} for col in returns.columns}
    return var_cvar

var_cvar = calculate_var_cvar(returns)
print("VaR et CVaR:\n", var_cvar)

# calculate_max_drawdown() : drawdown maximum (perte en %, durée, délai de récupération)
def calculate_max_drawdown(df):
    max_drawdown = {}
    # Calcul pour chaque actif du parametre drawdown
    for col in df.columns:
        roll_max = df[col].cummax()
        drawdown = (df[col] - roll_max) / roll_max
        max_dd = drawdown.min()
        end_date = drawdown.idxmin()
        # Trouver les dates de début et de récup. mais aussi le délai
        start_date = df[col][:end_date][df[col][:end_date] == roll_max[end_date]].idxmax()
        recovery_date = df[col][end_date:][df[col][end_date:] >= roll_max[end_date]].index
        recovery_time = (recovery_date[0] - end_date).days if not recovery_date.empty else np.nan
        # Stockage des résultats dans un dictionnaire
        max_drawdown[col] = {
            'Max Drawdown (%)': max_dd * 100,
            'Start Date': start_date,
            'End Date': end_date,
            'Recovery Time (days)': recovery_time
        }
    return max_drawdown

max_drawdown = calculate_max_drawdown(df_cleaned)
print("Max Drawdown:\n", max_drawdown)

# Créer un tableau de bord avec visualisations

# Global : graphique d’évolution des prix normalisés (base 100)
plt.figure(figsize=(14, 7))
for col in df_cleaned.columns:
    plt.plot(df_cleaned[col] / df_cleaned[col].iloc[0] * 100, label=col)
plt.title('Evolution des prix normalises (Base 100)')
plt.xlabel('Date')
plt.ylabel('Prix normalise')
plt.legend()
plt.show()

# Global : heatmap des corrélations entre actifs
plt.figure(figsize=(12, 10))
corr = returns.corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm')
plt.title('Heatmap des correlations entre actifs')
plt.show()

# Global : graphique rendement/risque (scatter plot)
plt.figure(figsize=(10, 6))
for i, txt in enumerate(returns.columns):
    plt.annotate(txt, (volatility.iloc[i], returns.mean().iloc[i] * 252))
plt.title('Rendement vs Risque')
plt.xlabel('Volatilite Annualisee')
plt.ylabel('Rendement Annualise')
plt.show()

# Pour un actif donné : distribution des rendements avec VaR/CVaR
asset = 'MSFT'  # Exemple avec l'actif "Microsoft"
plt.figure(figsize=(10, 6))
sns.histplot(returns[asset], bins=50, kde=True)
plt.axvline(var_cvar[0.95][asset]['VaR'], color='r', linestyle='--', label='VaR 95%')
plt.axvline(var_cvar[0.99][asset]['VaR'], color='g', linestyle='--', label='VaR 99%')
plt.title(f'Distribution des rendements de {asset}')
plt.xlabel('Rendement')
plt.ylabel('Frequence')
plt.legend()
plt.show()


# Partie 2 – Stratégies de trading et backtest


# Implémenter deux stratégies de trading basées sur des indicateurs techniques. Vous êtes libre de choisir les stratégies que vous souhaitez. Par exemple : Stratégie 1 : Moyenne mobile (ex: croisement MM courte/longue ou prix/MM) Stratégie 2 : Ichimoku avec règles d’entrée/sortie définies

# Stratégie 1 : Croisement de moyennes mobiles

# Fonction liée à cette stratégie
def moving_average_strategy(df, short_window=50, long_window=200):
    # Création du df des signaux
    signals = pd.DataFrame(index=df.index)
    signals['Price'] = df
    signals['Short_MA'] = df.rolling(window=short_window).mean()
    signals['Long_MA'] = df.rolling(window=long_window).mean()
    signals['Signal'] = 0.0
    signals.loc[signals.index[short_window:], 'Signal'] = np.where(
    signals['Short_MA'][short_window:] > signals['Long_MA'][short_window:], 1.0, 0.0
)
    # Positions 
    signals['Position'] = signals['Signal'].diff()
    return signals

print("\n Nous avons bien implemente la strategie de croisement de moyennes mobiles.", moving_average_strategy(df_cleaned['MSFT']).head())

# Stratégie 2 : Ichimoku

# Fonction liée à cette stratégie
def ichimoku_strategy(df):
    # Création du df des signaux
    signals = pd.DataFrame(index=df.index)
    signals['Price'] = df
    high_9 = df.rolling(window=9).max()
    low_9 = df.rolling(window=9).min()
    signals['Tenkan_Sen'] = (high_9 + low_9) / 2

    # Kijun-Sen (26 périodes)
    high_26 = df.rolling(window=26).max()
    low_26 = df.rolling(window=26).min()
    signals['Kijun_Sen'] = (high_26 + low_26) / 2

    # Signaux d'achat ou vente
    signals['Signal'] = 0.0
    signals['Signal'] = np.where(signals['Tenkan_Sen'] > signals['Kijun_Sen'], 1.0, 0.0)
    signals['Position'] = signals['Signal'].diff()
    return signals

print("\n Nous avons bien implemente la strategie Ichimoku.", ichimoku_strategy(df_cleaned['MSFT']).head())

#Développer le moteur de backtest : Génération des signaux d’achat/vente/conservation Gestion du portefeuille (positions, cash, transactions) Calcul des métriques de performance et de risque Performance des stratégies vs Buy & Hold pour chaque actif Analyse des corrélations entre stratégies Courbes de performance cumulée (stratégies vs benchmark) Drawdown dans le temps

# Fonction de backtest
def backtest_strategy(df, signals, initial_capital=10000):
    # Création du df 
    positions = pd.DataFrame(index=signals.index).fillna(0.0)
    positions['Asset'] = signals['Signal'] * 1  

    portfolio = positions.multiply(df, axis=0)
    pos_diff = positions.diff()

    # Calcul des valeurs 
    portfolio['Holdings'] = (positions.multiply(df, axis=0)).sum(axis=1)
    portfolio['Cash'] = initial_capital - (pos_diff.multiply(df, axis=0)).sum(axis=1).cumsum()
    portfolio['Total'] = portfolio['Holdings'] + portfolio['Cash']
    portfolio['Returns'] = portfolio['Total'].pct_change()

    return portfolio


# Backtest des deux stratégies sur un actif donné (ici Microsoft)
signals_ma = moving_average_strategy(df_cleaned['MSFT'])
portfolio_ma = backtest_strategy(df_cleaned['MSFT'], signals_ma)
print("\n Nous avons bien effectue le backtest de la strategie de moyennes mobiles.", portfolio_ma.head())
signals_ichi = ichimoku_strategy(df_cleaned['MSFT'])
portfolio_ichi = backtest_strategy(df_cleaned['MSFT'], signals_ichi)
print("\n Nous avons bien effectue le backtest de la strategie Ichimoku.", portfolio_ichi.head())

#Export en CSV des resultats de backtest
portfolio_ma.to_csv('Backtest_Moving_Average_MSFT.csv')
portfolio_ichi.to_csv('Backtest_Ichimoku_MSFT.csv')

# Optimisation des paramètres : Division des données : 70% entraînement, 30% test Sélection des paramètres optimaux sur l’échantillon d’entraînement (exemple : fenêtre d’observation des moyennes mobiles, seuil d’achat,et.)
def optimize_moving_average_params(df, short_windows, long_windows):
    # Choix des meilleurs parametres selon le Sharpe Ratio
    best_sharpe = -np.inf
    best_params = (0, 0)
    # Boucle sur les possibles combinaisons
    for short in short_windows:
        for long in long_windows:
            if short >= long:
                continue
            # Backtest avec certains parametres courants
            signals = moving_average_strategy(df, short_window=short, long_window=long)
            portfolio = backtest_strategy(df, signals)
            sharpe_ratio = (portfolio['Returns'].mean() / portfolio['Returns'].std()) * np.sqrt(252)
            # Maj des meilleurs parametres si le Sharpe ratio est superieur au meilleur 
            if sharpe_ratio > best_sharpe:
                best_sharpe = sharpe_ratio
                best_params = (short, long)
    return best_params, best_sharpe
# Optimisation des parametres 
short_windows = [20, 50, 100]
long_windows = [100, 200, 300]
best_params, best_sharpe = optimize_moving_average_params(df_cleaned['MSFT'], short_windows, long_windows)

print(f"\n Meilleurs parametres pour la strategie de moyennes mobiles: Short MA = {best_params[0]}, Long MA = {best_params[1]} avec un Sharpe Ratio de {best_sharpe:.2f}")

# Générer un rapport synthétique des résultats dans Excel. Ce rapport peut contenir des graphiques ou des formules Excel relié à une table écrit à la volée par Python / Pandas.
with pd.ExcelWriter('Rapport_Financier_Analyse.xlsx', engine='xlsxwriter') as writer:
    summary_df.to_excel(writer, sheet_name='Asset Summary', index=False)
    volatility.to_frame(name='Volatility').to_excel(writer, sheet_name='Volatility')
    pd.DataFrame(var_cvar).to_excel(writer, sheet_name='VaR_CVaR')
    pd.DataFrame(max_drawdown).to_excel(writer, sheet_name='Max Drawdown')
    portfolio_ma.to_excel(writer, sheet_name='MA Strategy Portfolio')
    portfolio_ichi.to_excel(writer, sheet_name='Ichimoku Strategy Portfolio')

print("\n Le rapport synthetique des resultats a ete genere dans 'Rapport_Financier_Analyse.xlsx'.")