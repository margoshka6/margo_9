import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split  # Імпортуємо функцію для розділення даних на тренувальну і тестову вибірки
from sklearn.preprocessing import StandardScaler  # Імпортуємо StandardScaler для нормалізації даних
from sklearn.neighbors import KNeighborsClassifier  # Імпортуємо K-Nearest Neighbors Classifier
from sklearn.metrics import confusion_matrix, accuracy_score  # Імпортуємо метрики оцінки моделі

df = pd.read_csv("train.csv")
print(df.info())
df["last_seen"]=pd.to_datetime(df["last_seen"], dayfirst=True,errors="coerce")
current_date=datetime.now()
df["days_since_last_seen"]=(current_date-df["last_seen"]).dt.days
# Аналіз кількості покупок залежно від статі
gender_group = df.groupby("gender")["result"].mean()
print(gender_group)

# Аналіз залежності від сімейного стану
relation_group = df.groupby("relation")["result"].mean()
print(relation_group)

# Заповнюємо пропущені дати народження медіанним роком
df["bdate"] = pd.to_datetime(df["bdate"], errors="coerce")
df["bdate_year"] = df["bdate"].dt.year.fillna(df["bdate"].dt.year.median())

# Створюємо ознаку віку
current_year = 2024
df["age"] = current_year - df["bdate_year"]

# Чи працює користувач
df["is_employed"] = df["career_end"] > df["career_start"]

df.drop(["id", "last_seen", "langs", "bdate", "career_end", "career_start"], axis=1, inplace=True)

def remove_False_life_main(row):
    if row["life_main"] == "False":
        return -1
    return int(row["life_main"])
def remove_False_people_main(row):
    if row["people_main"] == "False":
        return -1
    return int(row["people_main"])

df["life_main"] = df.apply(remove_False_life_main, axis=1)
df["people_main"] = df.apply(remove_False_people_main, axis=1)



# One-hot encoding для категоріальних змінних
df = pd.get_dummies(df, columns=["education_form", "education_status", "occupation_type"], drop_first=True)

print(df.info())

# Вибір цільової змінної та ознак
X = df.drop("result", axis=1)
y = df["result"]

# Розділення даних
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42)

# Навчання моделі
sc = StandardScaler()
X_train = sc.fit_transform(X_train)  # Нормалізуємо тренувальні дані
X_test = sc.transform(X_test)  # Нормалізуємо тестові дані на основі параметрів тренувальної вибірки

classifier = KNeighborsClassifier(n_neighbors=5)  # Створюємо модель K-Nearest Neighbors з 5 сусідами
classifier.fit(X_train, y_train)  # Навчаємо модель на тренувальних даних

y_pred = classifier.predict(X_test)  # Виконуємо прогнозування на тестових даних
print("Відсоток правильно передбачених результатів:",
      accuracy_score(y_test, y_pred) * 100)  # Виводимо точність моделі
print("Confusion matrix:")
cm = confusion_matrix(y_test, y_pred)
print(cm)  # Виводимо матрицю плутанини для оцінки моделі

print(cm[0][0], "- правильно класифіковані як ті, хто не придбав курс")
print(cm[0][1], "- помилково класифіковані як ті, хто придбав курс, хоча насправді вони його не придбали")
print(cm[1][0], "- помилково класифіковані як ті, хто не придбав курс, хоча насправді вони його придбали")
print(cm[1][1], "- правильно класифіковані як ті, хто придбав курс")

# зберігаємо дані для тесту в новий датафрейм
df2 = pd.read_csv("test.csv", encoding="utf-8", delimiter=";")
# зберігаємо лише ідентифікатор
ID = df2['id']
df2["last_seen"]=pd.to_datetime(df2["last_seen"], dayfirst=True,errors="coerce")
df2["days_since_last_seen"]=(current_date-df2["last_seen"]).dt.days
current_date=datetime.now()


# Заповнюємо пропущені дати народження медіанним роком
df2["bdate"] = pd.to_datetime(df2["bdate"], errors="coerce")
df2["bdate_year"] = (df2["bdate"].
                     dt.year.fillna(df2["bdate"].dt.year.median()))

# Створюємо ознаку віку
current_year = 2024
df2["age"] = current_year - df2["bdate_year"]

# Чи працює користувач
df2["is_employed"] = df2["career_end"] > df2["career_start"]

df2.drop(["id", "last_seen", "langs", "bdate",
          "career_end", "career_start"], axis=1, inplace=True)

def remove_False_life_main(row):
    if row["life_main"] not in "12345678910":
        return -1
    return int(row["life_main"])
def remove_False_people_main(row):
    if row["people_main"] not in "12345678910":
        return -1
    return int(row["people_main"])

df2["life_main"] = df2.apply(remove_False_life_main, axis=1)
df2["people_main"] = df2.apply(remove_False_people_main, axis=1)

# One-hot encoding для категоріальних змінних
df2 = pd.get_dummies(df2, columns=["education_form", "education_status", "occupation_type"], drop_first=True)


# класифікуємо ці данні
y_pred2 = classifier.predict(df2)

# формуємо датафрейм із двох стовпчиків
result = pd.DataFrame({'id': ID, 'result': y_pred2})

# зберігаємо в окреми CSV файл наш  результат із лише двома стовпчиками
result.to_csv("result.csv", index=False)






