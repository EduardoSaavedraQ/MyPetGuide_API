from services.ml.kmeans_service import predict_cluster
from utils.pet import preprocess_pet_data_for_clustering
import pandas as pd
import os
import pytest

TEST_DOGS_PATH = os.path.join(os.path.dirname(__file__), "../../../test_datasets/labeled_dogs.csv")
TEST_CATS_PATH = os.path.join(os.path.dirname(__file__), "../../../test_datasets/labeled_cats.csv")


@pytest.mark.parametrize(
    ("test_pet_data_path", "species"),
    [
        (TEST_DOGS_PATH, True),
        (TEST_CATS_PATH, False),
    ],
    ids=[
        "perros_test",
        "gatos_test",
    ]
)
def test_predict_cluster_predicts_correct_pet_cluster_for_dogs_and_cats(
    test_pet_data_path: str,
    species: bool
) -> None:
    df_pets = pd.read_csv(test_pet_data_path)

    for _, row in df_pets.iterrows():
        pet_data = row.to_dict()
        pet_data['species'] = species

        preprocessed_data: list = preprocess_pet_data_for_clustering(pet_data)

        predicted_cluster: list = predict_cluster(
            "dog" if species else "cat",
            preprocessed_data
        )

        try:
            assert predicted_cluster[0] == pet_data['pet_label']
        except AssertionError as e:
            pytest.fail(f"Fallo en la predicción del clúster para la mascota con id_registro {pet_data['id_registro']}\n{str(e)}")