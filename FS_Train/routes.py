from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db, EducationalProgram, Employee, TrainingAssignment, User, AccessRights, TrainingStatus
from schemas import EducationalProgramCreate, EducationalProgramResponse, EducationalProgramUpdate, EmployeeCreate, EmployeeResponse, EmployeeUpdate, TrainingAssignmentCreate, TrainingAssignmentResponse, TrainingAssignmentUpdate, UserCreate, UserResponse, UserUpdate, LoginRequest

router = APIRouter()

def get_current_user(db: Session = Depends(get_db)):
    return db.query(User).first()


# ====================== ГРУППА: АВТОРИЗАЦИЯ И ПОЛЬЗОВАТЕЛИ ======================

@router.post("/auth/register",
             response_model=UserResponse,
             status_code=status.HTTP_201_CREATED,
             tags=["Аутентификация и пользователи"],
             summary="Регистрация нового пользователя",
             description="Создание учетной записи пользователя системы")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже зарегистрирован"
        )
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=user.password,
        access_rights=user.access_rights,
        employee_id=user.employee_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/auth/login",
             tags=["Аутентификация и пользователи"],
             summary="Вход в систему",
             description="Аутентификация пользователя по email и паролю")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь с таким email не найден"
        )
    if user.password_hash != login_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль"
        )
    return {
        "message": "Успешный вход в систему",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "access_rights": user.access_rights
        },
        "token": "dummy_jwt_token"
    }


@router.get("/users/",
            response_model=List[UserResponse],
            tags=["Аутентификация и пользователи"],
            summary="Получить список пользователей",
            description="Только для администраторов и HR")
def read_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.access_rights not in [AccessRights.ADMIN, AccessRights.HR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра списка пользователей"
        )
    return db.query(User).all()


@router.delete("/users/{user_id}",
               tags=["Аутентификация и пользователи"],
               summary="Удалить пользователя",
               description="Только для администраторов")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.access_rights != AccessRights.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор может удалять пользователей"
        )
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить собственный аккаунт"
        )
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    db.delete(db_user)
    db.commit()
    return {"message": "Пользователь успешно удален"}


# ====================== ГРУППА: ОБРАЗОВАТЕЛЬНЫЕ ПРОГРАММЫ ======================

@router.post("/educational-programs/",
             response_model=EducationalProgramResponse,
             status_code=status.HTTP_201_CREATED,
             tags=["Образовательные программы"],
             summary="Создать образовательную программу",
             description="Добавление новой образовательной программы в систему")
def create_educational_program(
    program: EducationalProgramCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(EducationalProgram).filter(
        EducationalProgram.protocol_number == program.protocol_number
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Программа с таким номером протокола уже существует"
        )
    db_program = EducationalProgram(**program.model_dump())
    db.add(db_program)
    db.commit()
    db.refresh(db_program)
    return db_program


@router.get("/educational-programs/",
            response_model=List[EducationalProgramResponse],
            tags=["Образовательные программы"],
            summary="Получить список образовательных программ",
            description="Возвращает список всех образовательных программ с возможностью фильтрации по активности")
def read_educational_programs(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(EducationalProgram)
    if active_only:
        query = query.filter(EducationalProgram.is_active == True)
    return query.all()


@router.get("/educational-programs/{program_id}",
            response_model=EducationalProgramResponse,
            tags=["Образовательные программы"],
            summary="Получить образовательную программу по ID",
            description="Получение детальной информации о конкретной образовательной программе")
def read_educational_program(program_id: int, db: Session = Depends(get_db)):
    program = db.query(EducationalProgram).filter(EducationalProgram.id == program_id).first()
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Образовательная программа не найдена"
        )
    return program


@router.put("/educational-programs/{program_id}",
            response_model=EducationalProgramResponse,
            tags=["Образовательные программы"],
            summary="Обновить образовательную программу",
            description="Обновление информации о существующей образовательной программе")
def update_educational_program(
    program_id: int,
    program_update: EducationalProgramUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_program = db.query(EducationalProgram).filter(EducationalProgram.id == program_id).first()
    if not db_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Образовательная программа не найдена"
        )
    update_data = program_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_program, field, value)
    db.commit()
    db.refresh(db_program)
    return db_program


@router.delete("/educational-programs/{program_id}",
               tags=["Образовательные программы"],
               summary="Удалить образовательную программу",
               description="Удаление образовательной программы из системы")
def delete_educational_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_program = db.query(EducationalProgram).filter(EducationalProgram.id == program_id).first()
    if not db_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Образовательная программа не найдена"
        )
    db.delete(db_program)
    db.commit()
    return {"message": "Образовательная программа успешно удалена!"}


# ====================== ГРУППА: СОТРУДНИКИ ======================

@router.post("/employees/",
             response_model=EmployeeResponse,
             status_code=status.HTTP_201_CREATED,
             tags=["Сотрудники"],
             summary="Создать сотрудника",
             description="Добавление нового сотрудника в систему")
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Employee).filter(Employee.email == employee.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сотрудник с таким email уже существует"
        )
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


@router.get("/employees/",
            response_model=List[EmployeeResponse],
            tags=["Сотрудники"],
            summary="Получить список сотрудников",
            description="Возвращает список всех сотрудников компании")
def read_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()


@router.get("/employees/{employee_id}",
            response_model=EmployeeResponse,
            tags=["Сотрудники"],
            summary="Получить сотрудника по ID",
            description="Получение детальной информации о конкретном сотруднике")
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден"
        )
    return employee


@router.put("/employees/{employee_id}",
            response_model=EmployeeResponse,
            tags=["Сотрудники"],
            summary="Обновить данные сотрудника",
            description="Обновление информации о существующем сотруднике")
def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден"
        )
    update_data = employee_update.model_dump(exclude_unset=True)
    if 'email' in update_data and update_data['email'] != db_employee.email:
        existing = db.query(Employee).filter(
            Employee.email == update_data['email'],
            Employee.id != employee_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Сотрудник с таким email уже существует"
            )
    for field, value in update_data.items():
        setattr(db_employee, field, value)
    db.commit()
    db.refresh(db_employee)
    return db_employee


@router.delete("/employees/{employee_id}",
               tags=["Сотрудники"],
               summary="Удалить сотрудника",
               description="Удаление сотрудника из системы")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден"
        )
    db.delete(db_employee)
    db.commit()
    return {"message": "Сотрудник успешно удален!"}


# ====================== ГРУППА: НАЗНАЧЕНИЯ НА ОБУЧЕНИЕ ======================

@router.post("/training-assignments/",
             response_model=TrainingAssignmentResponse,
             status_code=status.HTTP_201_CREATED,
             tags=["Назначения на обучение"],
             summary="Создать назначение на обучение",
             description="Назначение сотрудника на образовательную программу")
def create_training_assignment(
    assignment: TrainingAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = db.query(Employee).filter(Employee.id == assignment.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден"
        )
    program = db.query(EducationalProgram).filter(EducationalProgram.id == assignment.education_id).first()
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Образовательная программа не найдена"
        )
    overlapping = db.query(TrainingAssignment).filter(
        TrainingAssignment.employee_id == assignment.employee_id,
        TrainingAssignment.education_id == assignment.education_id,
        TrainingAssignment.start_date <= assignment.end_date,
        TrainingAssignment.end_date >= assignment.start_date
    ).first()
    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сотрудник уже обучается на этой программе в указанный период"
        )
    db_assignment = TrainingAssignment(**assignment.model_dump())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


@router.get("/training-assignments/",
            response_model=List[TrainingAssignmentResponse],
            tags=["Назначения на обучение"],
            summary="Получить список назначений на обучение",
            description="Возвращает список всех назначений на обучение")
def read_training_assignments(db: Session = Depends(get_db)):
    return db.query(TrainingAssignment).all()


@router.get("/employees/{employee_id}/training-history",
            tags=["Назначения на обучение"],
            summary="Получить историю обучения сотрудника",
            description="Получение полной истории обучения конкретного сотрудника")
def read_employee_training_history(
    employee_id: int,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден в системе"
        )
    assignments = db.query(TrainingAssignment).filter(
        TrainingAssignment.employee_id == employee_id
    ).all()
    return {
        "employee": employee.full_name,
        "training_history": [
            {
                "program": assignment.educational_program.name,
                "start_date": assignment.start_date,
                "end_date": assignment.end_date,
                "status": assignment.status
            }
            for assignment in assignments
        ]
    }


@router.put("/training-assignments/{assignment_id}",
            response_model=TrainingAssignmentResponse,
            tags=["Назначения на обучение"],
            summary="Обновить назначение на обучение",
            description="Обновление информации о назначении на обучение")
def update_training_assignment(
    assignment_id: int,
    assignment_update: TrainingAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_assignment = db.query(TrainingAssignment).filter(TrainingAssignment.id == assignment_id).first()
    if not db_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Назначение на обучение не найдено"
        )
    update_data = assignment_update.model_dump(exclude_unset=True)
    if ('start_date' in update_data or 'end_date' in update_data):
        start_date = update_data.get('start_date', db_assignment.start_date)
        end_date = update_data.get('end_date', db_assignment.end_date)
        if end_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Дата окончания не может быть раньше даты начала"
            )
    for field, value in update_data.items():
        setattr(db_assignment, field, value)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment