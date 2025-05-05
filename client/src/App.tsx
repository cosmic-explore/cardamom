import { useState } from 'react'
import './App.css'
import { login, joinMatch, refreshMatch } from './utils/server-connection.tsx'
import { Button } from '@radix-ui/themes'
import { LoginPanel } from './components/LoginPanel.tsx'
import { MatchPanel } from './components/MatchPanel.tsx'
import { MatchData, PlayerData } from './DataTypes.tsx'

function App() {
  const [playerData, setPlayerData] = useState<PlayerData>()
  const [matchData, setMatchData] = useState<MatchData>()

  const handleLogin = (inputText : string) => {
    login(inputText).then((responseJson) => {
      console.log(responseJson)
      setPlayerData(responseJson)
    })
  }

  const handleJoinMatch = () => {
    joinMatch().then((matchStream: EventSource) => {
      matchStream.onopen = () => {
        console.log("connected to match stream")
      }
      matchStream.onmessage = (event) => {
        console.log("match event received")
        let data = JSON.parse(JSON.parse(event.data))
        console.log(data)
        if ((typeof data) != 'number') {
          setMatchData(data)
        } else {
          refreshMatch()
        }
      }
      matchStream.onerror = (error) => {
        console.log(error)
        console.log("closing match stream")
        matchStream.close()
      }
    })
  }

  return (
    <>
      <div className='flex'>
        <div className='flex flex-col items-start pr-5'>
          {playerData ? '' : <LoginPanel onSubmit={handleLogin}/>}
          {playerData ? <div>User: {playerData.name}</div> : ''}
        </div>
        <div className='grow-1'>
          {matchData && playerData ? <MatchPanel {...{matchData: matchData, playerData: playerData}}/> : ''}
          {playerData && !matchData ? <Button onClick={handleJoinMatch}>Join Match</Button> : ''} 
        </div>
      </div>
    </>
  )
}

export default App
