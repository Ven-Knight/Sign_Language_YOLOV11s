# ─────────────────────────────────────────────────────────────
# Data Validation Component — Structure Check + Status Logging
# ─────────────────────────────────────────────────────────────

import os
import sys
import shutil

from sign_lang.logger                  import logging
from sign_lang.exception               import AppException
from sign_lang.entity.config_entity    import DataValidationConfig
from sign_lang.entity.artifacts_entity import (
                                                DataIngestionArtifact,
                                                DataValidationArtifact
                                              )

# ─────────────────────────────────────────────────────────────
# Validates expected files in feature store directory
# ─────────────────────────────────────────────────────────────
class DataValidation:
    def __init__(
                    self,
                    data_ingestion_artifact : DataIngestionArtifact,
                    data_validation_config  : DataValidationConfig,
                ):
        try:
            self.data_ingestion_artifact    = data_ingestion_artifact
            self.data_validation_config     = data_validation_config
        except Exception as e:
            raise AppException(e, sys)

    
    # ─────────────────────────────────────────────────────────
    # Check if all required files exist in extracted dataset
    # ─────────────────────────────────────────────────────────
    def validate_all_files_exist(self) -> bool:
        try:
            # Ensure validation directory exists for status logging
            os.makedirs(self.data_validation_config.data_validation_dir, exist_ok=True)

            # Root path where Roboflow dataset was extracted
            base_path      = os.path.join(
                                            self.data_ingestion_artifact.feature_store_path,
                                            "Sign_Language_Images"
                                         )

            # Expected structure for YOLOv11 training
            required_paths = [
                                os.path.join(base_path, "train", "images"),   # training images
                                os.path.join(base_path, "train", "labels"),   # training labels
                                os.path.join(base_path, "valid", "images"),   # validation images
                                os.path.join(base_path, "valid", "labels"),   # validation labels
                                os.path.join(base_path, "data.yaml")          # YOLO config file
                             ]

            # Identify missing paths
            missing        = [path for path in required_paths if not os.path.exists(path)]

            # Validation passes only if all required paths exist
            validation_status = len(missing) == 0

            # Write status and missing paths to status.txt for auditability
            with open(self.data_validation_config.valid_status_file_dir, 'w') as f:
                f.write(f"Validation status : {validation_status}\n")
                if not validation_status:
                    f.write("Missing paths :\n")
                    for path in missing:
                        f.write(f"- {path}\n")

            return validation_status

        except Exception as e:
            raise AppException(e, sys)


    # ─────────────────────────────────────────────────────────
    # Orchestrates validation and returns artifact
    # ─────────────────────────────────────────────────────────
    def initiate_data_validation(self) -> DataValidationArtifact:
        logging.info("Starting data validation")

        try:
            status   = self.validate_all_files_exist()
            artifact = DataValidationArtifact(validation_status = status)

            logging.info(f"Validation completed: {artifact}")

            # Optionally copy zip file to working directory for traceability
            if status:
                shutil.copy(self.data_ingestion_artifact.data_zip_file_path, os.getcwd())

            return artifact

        except Exception as e:
            raise AppException(e, sys)