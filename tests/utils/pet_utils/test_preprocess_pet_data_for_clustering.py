from utils.pet import preprocess_pet_data_for_clustering
from services.ml.kmeans_service import predict_cluster
import pandas as pd
import os
import pytest

ORDERED_PREPROCESSED_FEATURES = [
    "sex", "pet_age", "vaccinated", "dewormed", "sterilized", "has_disability",
    "size_1", "size_2", "size_3", "size_4",
    "sociability_0", "sociability_1", "sociability_2", "sociability_3",
    "fur_length_0", "fur_length_1", "fur_length_2", "fur_length_3",
    "shedding_level_0", "shedding_level_1", "shedding_level_2", "shedding_level_3",
    "energy_level_1", "energy_level_2", "energy_level_3",
    "care_level_cost_1", "care_level_cost_2", "care_level_cost_3",
    "care_difficulty_1", "care_difficulty_2", "care_difficulty_3"
]

TEST_DOGS_PATH = os.path.join(os.path.dirname(__file__), "../../test_datasets/labeled_dogs.csv")
TEST_CATS_PATH = os.path.join(os.path.dirname(__file__), "../../test_datasets/labeled_cats.csv")
PREPROCESSED_TEST_DOGS_DATA_PATH = os.path.join(os.path.dirname(__file__), "../../test_datasets/processed_dogs.csv")
PREPROCESSED_TEST_CATS_DATA_PATH = os.path.join(os.path.dirname(__file__), "../../test_datasets/processed_cats.csv")

@pytest.mark.parametrize(
    ("test_pet_data_path", "preprocessed_test_pet_data_path", "species"),
    [
        (TEST_DOGS_PATH, PREPROCESSED_TEST_DOGS_DATA_PATH, True),
        (TEST_CATS_PATH, PREPROCESSED_TEST_CATS_DATA_PATH, False),
    ],
    ids=[
        "perros_test",
        "gatos_test",
    ]
)
def test_preprocess_pet_data_for_clustering_genera_las_listas_de_valores_esperados(
    test_pet_data_path: str,
    preprocessed_test_pet_data_path: str,
    species: bool
) -> None:

    df_dogs = pd.read_csv(test_pet_data_path)
    df_preprocessed_dogs = pd.read_csv(preprocessed_test_pet_data_path)

    for _, row in df_dogs.iterrows():
        pet_data = row.to_dict()
        pet_data['species'] = species

        preprocessed_data: list = preprocess_pet_data_for_clustering(pet_data)

        try:
            assert preprocessed_data == pytest.approx(
                df_preprocessed_dogs.loc[
                    df_preprocessed_dogs['id_registro'] == pet_data['id_registro'],
                    ORDERED_PREPROCESSED_FEATURES
                ].values.flatten().tolist()
            )

        except AssertionError as e:
            pytest.fail(f"Fallo en el preprocesamiento o predicción para el perro con id_registro {pet_data['id_registro']}\n{str(e)}")