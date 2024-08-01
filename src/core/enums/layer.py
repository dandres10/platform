from enum import Enum


class LAYER(str,Enum):
    I_D_R = "infrastructure/database/repositories"
    D_S_U_E = "domain/services/use_cases/entities"
    I_W_C_E = "infrastructure/web/controller/entities"
