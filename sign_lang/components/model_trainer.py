# ─────────────────────────────────────────────────────────────
# Model Trainer — YOLOv11 Training via Ultralytics API
# ─────────────────────────────────────────────────────────────

import os
import sys
import shutil
from ultralytics                       import YOLO

from sign_lang.logger                  import logger
from sign_lang.exception               import AppException
from sign_lang.entity.config_entity    import ModelTrainerConfig
from sign_lang.entity.artifacts_entity import ModelTrainerArtifact
from sign_lang.entity.artifacts_entity import DataIngestionArtifact
# ─────────────────────────────────────────────────────────────
# Trains YOLOv11 model using Ultralytics interface
# ─────────────────────────────────────────────────────────────
class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig):
        self.model_trainer_config = model_trainer_config

    # ─────────────────────────────────────────────────────────
    # Entry point for training — returns model artifact
    # ─────────────────────────────────────────────────────────
    def initiate_model_trainer(self, data_ingestion_artifact: DataIngestionArtifact) -> ModelTrainerArtifact:
        logger.info("Starting YOLOv11 training")

        try:
            # Load pretrained model
            model          = YOLO(self.model_trainer_config.weight_name)

            # Path to data.yaml file
            data_yaml_path = os.path.join(
                                            data_ingestion_artifact.feature_store_path,
                                            "Sign_Language_Images",
                                            "data.yaml"
                                         )


            # Train using data.yaml and config params
            model.train(
                            data   = data_yaml_path,
                            epochs = self.model_trainer_config.no_epochs,
                            batch  = self.model_trainer_config.batch_size,
                            imgsz  = 416,
                            name   = "yolov11_sign_language",
                            cache  = True
                        )

            # Log training configuration for traceability
            logger.info(f"Training config — epochs: {self.model_trainer_config.no_epochs}, batch size: {self.model_trainer_config.batch_size}")
            
            # Dynamically locate best.pt from YOLO's save_dir
            output_dir       = model.trainer.save_dir                        # Automatically set by Ultralytics
            best_model_path  = os.path.join(output_dir, "weights", "best.pt")

            # Save to model_trainer_dir
            os.makedirs(self.model_trainer_config.model_trainer_dir, exist_ok=True)
            
            final_model_path = os.path.join(self.model_trainer_config.model_trainer_dir, "best.pt")
            
            # Ensure best.pt exists before attempting to copy
            if not os.path.exists(best_model_path):
                raise AppException(f"Training failed: best.pt not found at {best_model_path}", sys)
            
            shutil.copy(best_model_path, final_model_path)

            # Return artifact
            artifact         = ModelTrainerArtifact(trained_model_file_path=final_model_path)
            logger.info(f"Model training completed: {artifact}")
            return artifact

        except Exception as e:
            raise AppException(e, sys)