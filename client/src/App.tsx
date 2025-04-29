import { useState } from 'react'
import './App.css'
import { login, joinMatch, refreshMatch } from './utils/server-connection.tsx'
import { Button } from '@radix-ui/themes'
import { OrderPanel } from './components/OrderPanel.tsx'
import { LoginPanel } from './components/LoginPanel.tsx'
import { MatchPanel } from './components/MatchPanel.tsx'
import { MatchData, PlayerData } from './DataTypes.tsx'

function App() {
  const [playerData, setPlayerData] = useState<PlayerData>()
  const [matchData, setMatchData] = useState<MatchData>()
  const [inMatch, setInMatch] = useState<Boolean>(false)

  const handleLogin = (inputText : string) => {
    login(inputText).then((responseJson) =>{
      console.log(responseJson)
      setPlayerData(responseJson)
    })
  }

  const handleJoinMatch = () => {
    joinMatch().then((matchStream: EventSource) => {
      matchStream.onopen = () => {
        setInMatch(true)
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
        setInMatch(false)
      }
    })
  }

  const handleRefreshMatch = () => {
    refreshMatch()
  }

  return (
    <>
      <div className='flex'>
        <div className='flex flex-col items-start grow-1'>
          {playerData ? '' : <LoginPanel onSubmit={handleLogin}/>}
          {playerData ? <div>User: {playerData.name}</div> : ''}
        </div>
        <div className='grow-1'>
          {matchData ? <MatchPanel {...matchData}/> : ''}
          {playerData && !matchData ? <Button onClick={handleJoinMatch}>Join Match</Button> : ''} 
        </div>
        <div className='flex flex-col items-end grow-1'>
          {playerData && matchData ? <OrderPanel {...{currentPlayer: playerData, matchData}}/> : ''}
          {inMatch ? <Button onClick={handleRefreshMatch}>Refresh Match Data</Button> : '' }
        </div>
      </div>
    </>
  )
}

export default App
