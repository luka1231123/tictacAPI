# tictacAPI
this is a tic tac api;

/start starts a new game and returns a game_ID integer which is crucial to playing the game later



/move/{game_id} changes a place on the board from '.' to 'X' or 'O'. the syntax is like this: 

  curl -X POST http://{adress}/move/47 -H "Content-Type: application/json" -d '{ "type": "X", "position": 1 }'


  
/check/{game_id} checks if the game is finished or not and if it is finished it tells you the winner




/history gives you every movement and it's player.



//გამორთულია ამჟამად


the adress that you can POST or GET to is right now: 

  https://72ed-212-58-120-4.ngrok-free.app
  
so if you want to check history of the api it's like this:

  curl -X GET https://72ed-212-58-120-4.ngrok-free.app/history
  
and POST-ing start looks like this:

  curl -X POST https://72ed-212-58-120-4.ngrok-free.app/start




This is obviously temporary but i'm gonna keep it online for a few days to test.
