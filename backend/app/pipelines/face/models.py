import dlib
import face_recognition_models

class FaceModels:
    """
    A class to encapsulate the face recognition models.
    """

    def __init__(self):
        self.face_detector = dlib.get_frontal_face_detector()
        self.shape_predictor = dlib.shape_predictor(face_recognition_models.pose_predictor_model_location())
        self.face_recognition_model = dlib.face_recognition_model_v1(face_recognition_models.face_recognition_model_location())


face_models = FaceModels()