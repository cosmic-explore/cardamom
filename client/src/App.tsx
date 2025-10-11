import { useState } from 'react'
import './App.css'
import { login, joinMatch, refreshMatch, getPlayerMatches } from './utils/server-connection.tsx'
import { Button } from '@radix-ui/themes'
import { LoginPanel } from './components/LoginPanel.tsx'
import { CommandState, MatchPanel } from './components/MatchPanel.tsx'
import { MatchData, PlayerData, PlayerMatches } from './DataTypes.tsx'
import { COMMAND_UPDATE, MATCH_UPDATE } from './constants/game-constants.tsx'
import { getMatchCreature } from './utils/game-utils.tsx'

function App() {
    const [playerData, setPlayerData] = useState<PlayerData>()
    const [playerMatches, setPlayerMatches] = useState<PlayerMatches>()
    const [matchData, setMatchData] = useState<MatchData>()
    const [commandState, setCommandState] = useState<CommandState>({
        p1Submitted: false,
        p2Submitted: false
    })

    const handleLogin = async (inputText: string) => {
        const playerData = await login(inputText)
        console.log(playerData)
        setPlayerData(playerData)

        const matchData = await getPlayerMatches()
        console.log(matchData)
        setPlayerMatches(matchData)
    }

    const handleJoinMatch = () => {
        joinMatch().then((matchStream: EventSource) => {
            matchStream.onopen = () => {
                console.log('connected to match stream')
            }
            matchStream.onmessage = (event) => {
                console.log('match event received')
                const data = JSON.parse(JSON.parse(event.data))
                if (typeof data == 'number') {
                    // the success code for subscribing to the match is '1'
                    // ask the server for the current match state after subscribing
                    refreshMatch()
                } else {
                    console.log(data)
                    switch (data.notification_type) {
                        case MATCH_UPDATE:
                            const matchUpdate = JSON.parse(data.data)
                            console.log(matchUpdate)
                            setMatchData(enchanceMatchData(matchUpdate))
                            break
                        case COMMAND_UPDATE:
                            setCommandState({
                                p1Submitted: data.data.player_1,
                                p2Submitted: data.data.player_2
                            })
                            break
                    }
                }
            }
            matchStream.onerror = (error) => {
                console.log(error)
                console.log('closing match stream')
                matchStream.close()
                setMatchData(undefined) // kicks the user out of the match display
            }
        })
    }

    return (
        <>
            <div className="flex">
                <div className="flex flex-col items-start pr-5">
                    {playerData ? '' : <LoginPanel onSubmit={handleLogin} />}
                    {playerData ? <div>User: {playerData.name}</div> : ''}
                </div>
                {matchData && playerData ? (
                    <div className="grow-1">
                        <MatchPanel {...{ matchData, playerData, commandState }} />
                    </div>
                ) : (
                    ''
                )}
                {playerData && !matchData ? (
                    <div className="flex flex-row grow-1">
                        <div className="grow-1">
                            {playerMatches?.current ? (
                                <Button style={{ cursor: 'pointer' }} onClick={handleJoinMatch}>
                                    Rejoin Active Match
                                </Button>
                            ) : (
                                <Button style={{ cursor: 'pointer' }} onClick={handleJoinMatch}>
                                    Join Match
                                </Button>
                            )}
                        </div>
                        <div>
                            <h2>Finished Matches</h2>
                            {playerMatches?.finished?.map((matchId) => (
                                <li key={matchId}>{matchId}</li>
                            ))}
                        </div>
                    </div>
                ) : (
                    ''
                )}
            </div>
        </>
    )
}

const enchanceMatchData = (matchData: MatchData): MatchData => {
    matchData.creature_states = matchData.creature_states.map((cs) => {
        return { ...cs, creature: getMatchCreature(matchData, cs.creature_id) }
    })
    return matchData
}

export default App
