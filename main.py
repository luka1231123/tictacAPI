from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import json

app = FastAPI()

db_params = {
    "dbname": "tictacdb",
    "user": "postgres",
    "password": "1",
    "host": "localhost",
    "port": "5432"
}

# Helper function to execute SQL queries
def execute_query(query, params=None, fetch=True):
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute(query, params)
    connection.commit()
    result = None
    if fetch:
        result = cursor.fetchall()
    cursor.close()
    connection.close()
    print("Query:", query)
    print("Params:", params)
    print("Result:", result)
    return result[0] if (result and len(result) > 0) else None
#this is horrible; EW EW EW EW
def just_return(query, params=None, fetch=True):
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute(query, params)
    connection.commit()
    result = None
    if fetch:
        result = cursor.fetchall()
    cursor.close()
    connection.close()
    print("Query:", query)
    print("Params:", params)
    print("Result:", result)
    return result
# Models
class Move(BaseModel):
    type: str
    position: int


#idk if this does anything anymore. 
#I think it lost it's purpose but i am afraid to remove it
class Game(BaseModel):
    game: str
    winner: str = None



@app.post("/start", response_model=int)
def start_game():
    query = "INSERT INTO games DEFAULT VALUES RETURNING id;"
    tup = execute_query(query,fetch=True)
    game_id = tup[0]
    return game_id

@app.post("/move/{game_id}", response_model=dict)
def make_move(game_id: int, move: Move):
    query = "SELECT board FROM games WHERE id = %s;"
    result = execute_query(query, (game_id,))

    if not result:
        raise HTTPException(status_code=404, detail="Game not found.")

    board_str = result[0]

    if board_str is None:
        raise HTTPException(status_code=500, detail="Invalid board data in the database.")

    board = list(board_str)

    print("Received move for game_id:", game_id)
    print("Position to be played:", move.position)
    print("Current board:", board)

    position = move.position
    player = move.type

    if not (0 <= position < 9):
        raise HTTPException(status_code=400, detail="Invalid position.")

    if board[position] != ".":
        raise HTTPException(status_code=400, detail="Invalid position.")

    board[position] = player
    jsonBoard = json.dumps(board)

    query = "UPDATE games SET board = %s WHERE id = %s;"
    execute_query(query, (jsonBoard, game_id),fetch = False)

    query = "INSERT INTO game_moves (game_id, type, position) VALUES (%s, %s, %s);"
    execute_query(query, (game_id, player, position), fetch=False)

    return {"result": "success"}



@app.get("/check/{game_id}", response_model=Game)
def check_game(game_id: int):
    query = "SELECT * FROM games WHERE id = %s;"
    result = execute_query(query, (game_id,))
    
    if not result:
        raise HTTPException(status_code=404, detail="Game not found.")
    
    board = result[1]
    winner = check_winner(board)
    
    if winner:
        return {"game": "finished", "winner": winner}
    elif "." not in board:
        return {"game": "finished", "winner": None}
    else:
        return {"game": "in_progress"}

def check_winner(board):
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]             # Diagonals
    ]
    
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]] != ".":
            return board[condition[0]]
    
    return None

@app.get("/history", response_model=dict)
def get_history():
    query = "SELECT game_id, type, position FROM game_moves;"
    result = just_return(query)
    history = {}
    for game_id, move_type, position in result:
        if game_id not in history:
            history[game_id] = [{"type": move_type, "position": position}]
        else:
            history[game_id].append({"type": move_type, "position": position})
    return history