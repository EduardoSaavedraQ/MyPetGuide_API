from services.ml.knn_service import predict_compatible_clusters, get_knn_classes
from utils.user import preprocess_user_data_for_prediction
import pandas as pd
import os
import pytest

TEST_OWNERS_WITH_DOGS_PATH = os.path.join(os.path.dirname(__file__), "../../../test_datasets/owners/no_processed_owners_with_dogs_predictions.csv")
TEST_OWNERS_WITH_CATS_PATH = os.path.join(os.path.dirname(__file__), "../../../test_datasets/owners/no_processed_owners_with_cats_predictions.csv")

@pytest.mark.parametrize(
    ("test_owners_data_path", "model_type"),
    [
        (TEST_OWNERS_WITH_DOGS_PATH, "user_to_dogs"),
        (TEST_OWNERS_WITH_CATS_PATH, "user_to_cats")
    ],
    ids=["usuarios_con_perros", "usuarios_con_gatos"]
)
def test_predict_compatible_clusters_predice_el_cluster_mas_probable_esperado(
    test_owners_data_path: str,
    model_type: str
) -> None:

    df_owners = pd.read_csv(test_owners_data_path)
    knn_classes = get_knn_classes(model_type)

    for _, row in df_owners.iterrows():
        owner_data: dict = row.to_dict()

        preprocessed_data: list = preprocess_user_data_for_prediction(owner_data)

        predictions = predict_compatible_clusters(model_type, preprocessed_data)[0]

        greater_proba_index: int = 0

        for i in range(1, len(knn_classes)):
            if predictions[i] > predictions[greater_proba_index]:
                greater_proba_index = i

        try:
            assert row["predicted_pet_cluster"] == knn_classes[greater_proba_index]

        except AssertionError as e:
            pytest.fail(f"Error al predecir el clúster de mascota compatible para el registro con id {row["id_registro"]}\n{str(e)}")