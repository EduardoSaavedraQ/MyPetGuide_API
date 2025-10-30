from utils.user import preprocess_user_data_for_prediction
import pandas as pd
import os
import pytest

ORDERED_PREPROCESSED_FEATURES = [
    "house_size", "house_backyard_size", "family_size", "age",
    "available_time_per_day", "activity_level_1", "activity_level_2", "activity_level_3",
    "experience_with_pets_0", "experience_with_pets_1", "experience_with_pets_2", "experience_with_pets_3",
    "has_kids", "has_neighbors", "vet_access", "has_other_pets"
]

TEST_OWNERS_WITH_DOGS_PATH = os.path.join(os.path.dirname(__file__), "../../test_datasets/owners/no_processed_owners_with_dogs_predictions.csv")
TEST_OWNERS_WITH_CATS_PATH = os.path.join(os.path.dirname(__file__), "../../test_datasets/owners/no_processed_owners_with_cats_predictions.csv")
PREPROCESSED_TEST_OWNERS_WITH_DOGS_PATH = os.path.join(os.path.dirname(__file__), "../../test_datasets/owners/processed_owners_with_dogs_predictions.csv")
PREPROCESSED_TEST_OWNERS_WITH_CATS_PATH = os.path.join(os.path.dirname(__file__), "../../test_datasets/owners/processed_owners_with_cats_predictions.csv")

@pytest.mark.parametrize(
    ("test_owner_data_path", "preprocessed_test_owner_data_path"),
    [
        (TEST_OWNERS_WITH_DOGS_PATH, PREPROCESSED_TEST_OWNERS_WITH_DOGS_PATH),
        (TEST_OWNERS_WITH_CATS_PATH, PREPROCESSED_TEST_OWNERS_WITH_CATS_PATH)
    ],
    ids=["usuarios_con_perros", "usuarios_con_gatos"]
)
def test_preprocess_user_data_for_prediction(
    test_owner_data_path: str,
    preprocessed_test_owner_data_path: str
) -> None:

    df_owners = pd.read_csv(test_owner_data_path)
    df_preprocessed_owners = pd.read_csv(preprocessed_test_owner_data_path)

    for _, row in df_owners.iterrows():
        owner_data: dict = row.to_dict()

        preprocessed_data: list = preprocess_user_data_for_prediction(owner_data)

        try:
            assert preprocessed_data == pytest.approx(
                df_preprocessed_owners.loc[
                    df_preprocessed_owners["id_registro"] == owner_data["id_registro"],
                    ORDERED_PREPROCESSED_FEATURES
                ].values.flatten().tolist()
            )

        except AssertionError as e:
            pytest.fail(f"Fallo en el preprocesamiento para el dueño con id_registro {owner_data["id_registro"]}\n{str(e)}")