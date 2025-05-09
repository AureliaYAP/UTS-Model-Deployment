# -*- coding: utf-8 -*-
"""UTS Model Deployment.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/11mUY8Hk4n8u_hmQulvgPzGwXzFUYnwnJ

# Library
"""

import pandas as pd
import numpy as np


"""# Dataset"""

df=pd.read_csv('Dataset_A_loan.csv')
df.head()

df.info()

df.describe()

"""Memberi informasi jumlah nilai yang tidak hilang di setiap kolom (count), rata-rata nilai di setiap kolom (mean), stander deviasi atau seberapa tersebarnya data(std), nilai minimum setiap kolom (min), kuartil pertama (25%), median (50%), kuartil ketiga (75%), dan nilai maksimum setiap kolom (max)

# Pre-Processing Dataset (Pt.1)

## cek for missing value
"""

df.isnull().sum()

"""## Mengisi person_income yang kosong dengan median dari person_income"""

median=df['person_income'].median()
df['person_income'].fillna(median, inplace=True)

df.isnull().sum()

"""## Encoding

Mencari kata-kata yang ada pada objek untuk di encoding
"""

print("Jenis-jenis kata pada person_gender:", df['person_gender'].unique())
print("Jenis-jenis kata pada person_education:", df['person_education'].unique())
print("Jenis-jenis kata pada person_home_ownership:", df['person_home_ownership'].unique())
print("Jenis-jenis kata pada loan_intent:", df['loan_intent'].unique())
print("Jenis-jenis kata pada previous_loan_defaults_on_file:", df['previous_loan_defaults_on_file'].unique())

"""Melakukan normalisasi teks agar 'female' dengan 'fe male' memiliki arti yang sama serta 'male' dengan 'Male' memiliki arti yang sama"""

def clean_gender(g):
    if pd.isna(g):
        return np.nan
    g = g.lower().replace(" ", "")
    if g == 'male':
        return 'male'
    elif g == 'female':
        return 'female'
    else:
        return np.nan

df['person_gender'] = df['person_gender'].apply(clean_gender)

"""### Binary Encoding untuk variabel biner"""

df['person_gender'] = df['person_gender'].map({'male': 1, 'female': 0})
df['previous_loan_defaults_on_file'] = df['previous_loan_defaults_on_file'].map({'Yes': 1, 'No': 0})

"""### One-hot encoding untuk multi kategori"""

df = pd.get_dummies(df, columns=[
    'person_education',
    'person_home_ownership',
    'loan_intent'
], prefix=[
    'edu', 'home', 'intent'
], drop_first=True)

"""Melihat dan memastikan nama kolom pada dataset sudah sesuai"""

df.head()

"""## Checking duplicate values"""

df.duplicated().sum()

"""## Check distribution of each numeric columns

Untuk memahami karakteristik data
"""

def check_distribution_outliers(df, columns):
    for col in columns:
        plt.figure(figsize=(10, 3))

        # Histogram
        plt.subplot(1, 2, 1)
        sns.histplot(df[col], bins=30)
        plt.title('Histogram')

        # Boxplot
        plt.subplot(1, 2, 2)
        sns.boxplot(y=df[col])
        plt.title('Boxplot')

        plt.show()

check_distribution_outliers(df, df.columns)

"""# EDA

Heatmap (cari cara jelasin heatmap)
"""

plt.figure(figsize = (33,17))
corr = df.corr()
sns.heatmap(corr, annot = True, cmap = 'Blues', linewidths = 0.01, linecolor = 'black',
            fmt = '0.2f', annot_kws = {'fontsize' : 20})
plt.yticks(fontsize = 22, rotation = 0)
plt.xticks(fontsize = 22, rotation = 90)
plt.show()

"""# Pre-Processing"""

# Split test and training data
X = df.drop(columns=['loan_status'])
y = df['loan_status']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standard Scaler -> normal dist
standard_scaler_col = ['person_age', 'person_income', 'loan_amnt', 'loan_int_rate', 'credit_score']
standard_scaler = StandardScaler()
X_train[standard_scaler_col] = standard_scaler.fit_transform(X_train[standard_scaler_col])
X_test[standard_scaler_col] = standard_scaler.transform(X_test[standard_scaler_col])

"""# Modeling

## Random Forest
"""

# Random Forest
rf = RandomForestClassifier(random_state=42, max_depth=10, n_estimators=100)  # Set desired hyperparameters directly
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)

print("Classification Report (Random Forest):")
print(classification_report(y_test, y_pred_rf))
print("F1 Score (Random Forest):", f1_score(y_test, y_pred_rf))
print(confusion_matrix(y_test, y_pred_rf))

# AUC Curve
best_rf = rf
y_pred_proba = best_rf.predict_proba(X_test)[:, 1]
fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
roc_auc = roc_auc_score(y_test, y_pred_proba)
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {roc_auc:.2f})', color='darkorange', lw=2)
plt.plot([0, 1], [0, 1], linestyle='--', color='navy', lw=2)
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve Using Random Forest')
plt.legend(loc='lower right')
plt.show()

"""**Dari Grafik diatas, kita dapat menyimpulkan:**

Model Random Forest memiliki kemampuan prediksi yang sangat kuat dengan AUC 0.97, bisa dikatakan bahwa model ini bisa membedakan hampir semua kasus “disetujui” vs “ditolak” pinjaman dengan akurat.

## XGBoost
"""

# XGBoost
xgb = XGBClassifier(random_state=42, max_depth=3, n_estimators=100, learning_rate=0.1) # Set desired hyperparameters directly
xgb.fit(X_train, y_train)
y_pred_xgb = xgb.predict(X_test)

print("\nClassification Report (XGBoost):")
print(classification_report(y_test, y_pred_xgb))
print("F1 Score (XGBoost):", f1_score(y_test, y_pred_xgb))
print(confusion_matrix(y_test, y_pred_xgb))

# AUC Curve
y_pred_proba = xgb.predict_proba(X_test)[:, 1] # Changed best_xgb to xgb
fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
roc_auc = roc_auc_score(y_test, y_pred_proba)
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {roc_auc:.2f})', color='darkorange', lw=2)
plt.plot([0, 1], [0, 1], linestyle='--', color='navy', lw=2)
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve Using XGBoost')
plt.legend(loc='lower right')
plt.show()

"""Dengan AUC 0.97, Baik Random Forest maupun XGBoost sama-sama unggul dalam membedakan antara pinjaman yang disetujui vs ditolak.

## Model performance comparisons across classes
"""

models = ['Random Forest', 'XGBoost']
precision_0 = [0.96, 0.97]
recall_0 = [0.97, 0.99]
f1_0 = [0.94, 0.98]
precision_1 = [0.67, 0.97]
recall_1 = [0.39, 0.71]
f1_1 = [0.49, 0.82]

x = range(len(models))

plt.figure(figsize=(10, 5))
plt.bar(x, precision_0, width=0.25, color='lightcoral', label='Precision')
plt.bar([i + 0.25 for i in x], recall_0, width=0.25, color='indianred', label='Recall')
plt.bar([i + 0.5 for i in x], f1_0, width=0.25, color='brown', label='F1-Score')
plt.xticks([i + 0.25 for i in x], models)
plt.title('Class 0 Metrics')
plt.legend()
plt.show()

plt.figure(figsize=(10, 5))
plt.bar(x, precision_1, width=0.25, color='lightblue', label='Precision')
plt.bar([i + 0.25 for i in x], recall_1, width=0.25, color='skyblue', label='Recall')
plt.bar([i + 0.5 for i in x], f1_1, width=0.25, color='steelblue', label='F1-Score')
plt.xticks([i + 0.25 for i in x], models)
plt.title('Class 1 Metrics')
plt.legend()
plt.show()

"""**Untuk "Class 0 Metrics":**

* Kedua model sangat akurat dalam mengenali kelas 0 (misalnya, peminjam berisiko). Namun, XGBoost tetap lebih unggul secara keseluruhan, karena lebih baik untuk Kelas 0 (negatif)
* Model ini sangat ideal jika kamu ingin menghindari false negative (misalnya, salah memberikan pinjaman ke peminjam berisiko) dan tetap mampu mengenali peminjam yang layak.

**Untuk "Class 1 Metrics":**

* XGBoost lebih unggul dalam mengidentifikasi kelas 1 (misalnya, peminjam yang layak) dan lebih cocok digunakan ketika deteksi benar terhadap kelas positif penting (misalnya untuk menghindari risiko kredit macet).
* Random Forest bisa jadi terlalu berhati-hati sehingga banyak melewatkan kasus positif.
"""
