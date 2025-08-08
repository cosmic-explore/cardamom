import { useEffect, useState } from 'react'
import {
    ActionData,
    CommandData,
    CreatureState,
    MatchData,
    PlayerData,
    PositionData
} from '../DataTypes'
import { Board } from './Board'
import { Button, ThickCheckIcon } from '@radix-ui/themes'
import { OrderPanel } from './OrderPanel'
import { DetailPanel } from './DetailPanel'
import {
    getActionAffected,
    getActionTargets,
    getCreatureMoveRoute,
    getCreatureMoves,
    getStoredCommands,
    refreshMatch
} from '../utils/server-connection'
import { arePositionsSame, getActivePlayer, getMatchCreatureState } from '../utils/game-utils'

export type CommandState = {
    p1Submitted: boolean
    p2Submitted: boolean
}

export const MatchPanel = (props: {
    matchData: MatchData
    playerData: PlayerData
    commandState: CommandState
}) => {
    const [selectedPos, setSelectedPos] = useState<PositionData | null>(null)
    const [highlightedPosList, setHighlightedPosList] = useState<PositionData[]>([])
    const [commandMode, setCommandMode] = useState<string>('move')
    const [commands, setCommands] = useState<CommandData[]>(
        fillBlankCommands(props.matchData, props.playerData.name)
    )
    const [replayingTurn, setReplayingTurn] = useState<boolean>(false)

    useEffect(() => {
        getStoredCommands().then((data) => {
            if (data.length !== 0) {
                setCommands(data)
            } else {
                setCommands(fillBlankCommands(props.matchData, props.playerData.name))
            }
        })
    }, [props.commandState])

    useEffect(() => {
        updatePositionHighlights()
    }, [selectedPos, commandMode, commands])

    useEffect(() => {
        setSelectedPos(null)
        updatePositionHighlights()
        if (props.matchData.turn_number > 0) {
            setReplayingTurn(true)
        }
    }, [props.matchData])

    const updatePositionHighlights = () => {
        // TODO: use action id instead of name
        // highlight the appropriate positions if a creature is selected
        setHighlightedPosList([])

        if (selectedPos?.creature_state_id != null) {
            const creatureState = getCreatureStateFromId(selectedPos.creature_state_id)
            const targetedPos = getTargetedPos()
            if (commandMode === 'move') {
                if (targetedPos === null) {
                    // ask the server for the possible moves
                    getCreatureMoves(creatureState.id).then((response) => {
                        setHighlightedPosList(response)
                    })
                } else {
                    getCreatureMoveRoute(creatureState.id, {
                        target_x: targetedPos?.x.toString(),
                        target_y: targetedPos.y.toString()
                    }).then((response) => {
                        setHighlightedPosList(response)
                    })
                }
            } else {
                // commandMode === 'action'
                const currentAction = getCurrentAction()
                if (!currentAction) return

                if (targetedPos === null) {
                    // show all the positions in range to target
                    getActionTargets(creatureState.id, currentAction.id).then((response) => {
                        setHighlightedPosList(response)
                    })
                } else {
                    // show all the positions that will be affected by the action
                    getActionAffected(creatureState.id, currentAction.id, {
                        target_x: targetedPos?.x.toString(),
                        target_y: targetedPos.y.toString()
                    }).then((response) => {
                        setHighlightedPosList(response)
                    })
                }
            }
        }
    }

    const getCreatureStateFromId = (creatureStateId: string): CreatureState => {
        return getMatchCreatureState(props.matchData, creatureStateId)
    }

    const getTargetedPos = (): PositionData | null => {
        if (selectedPos?.creature_state_id) {
            const command = getCreatureCommand(
                getCreatureStateFromId(selectedPos.creature_state_id)
            )
            return commandMode === 'move' ? command.move_target : command.action_target
        } else {
            return null
        }
    }

    const getCurrentAction = (): ActionData | null => {
        if (selectedPos?.creature_state_id) {
            return getCreatureCommand(getCreatureStateFromId(selectedPos.creature_state_id)).action
        } else {
            return null
        }
    }

    const getCreatureCommand = (creatureState: CreatureState): CommandData => {
        let command = commands.find((c) => c.creature_state_id === creatureState.id)
        if (!command) {
            command = {
                creature_state_id: creatureState.id,
                move_target: null,
                action: null,
                action_target: null
            }
        }
        return command
    }

    const updateCommand = (
        updatingCommand: CommandData,
        newTarget: PositionData | null,
        action: ActionData | null
    ) => {
        // removes the existing command for a creature and inserts the new one
        if (commandMode === 'move') {
            updatingCommand.move_target = newTarget
        } else {
            // commandMode = 'action'
            updatingCommand.action = action
            updatingCommand.action_target = newTarget
        }

        const newCommands = commands.filter(
            (c) => c.creature_state_id !== updatingCommand.creature_state_id
        )
        newCommands.push(updatingCommand)
        setCommands(newCommands)
    }

    const isOwnedCreature = (creatureId: string): boolean => {
        return props.playerData.creatures.some((c) => c.id === creatureId)
    }

    const isControlledCreatureState = (creatureStateId: string): boolean => {
        const creatureState = getCreatureStateFromId(creatureStateId)
        return props.playerData.id === creatureState.creature.player_id
    }

    const isPositionIn = (pos: PositionData, posList: PositionData[]): boolean => {
        return posList.some((p) => arePositionsSame(p, pos))
    }

    const handlePosClick = async (posData: PositionData) => {
        // if the position of one of the player's creatures is selected, set a target of its
        // command if the clicked position is within the command's range
        if (
            selectedPos?.creature_state_id &&
            isControlledCreatureState(selectedPos.creature_state_id)
        ) {
            const command = getCreatureCommand(
                getCreatureStateFromId(selectedPos.creature_state_id)
            )
            const targetedPos = getTargetedPos()

            if (targetedPos === null) {
                if (isPositionIn(posData, highlightedPosList)) {
                    // set the target
                    updateCommand(command, posData, command.action)
                    return
                }
            } else if (arePositionsSame(posData, targetedPos)) {
                // clear the target
                updateCommand(command, null, command.action)
                return
            }
        }

        setSelectedPos(posData)
    }

    const handleOrderBoxClick = (creatureState: CreatureState) => {
        creatureState.position.creature_state_id = creatureState.id
        setSelectedPos(creatureState.position)
    }

    const playerCommandState =
        props.playerData.id === props.matchData.player_1?.id
            ? props.commandState.p1Submitted
            : props.commandState.p2Submitted

    return (
        <div className="flex flex-row">
            <div className="flex flex-col items-center">
                <div className="mb-1">{props.matchData.id}</div>
                <div>Turn {props.matchData.turn_number}</div>
                <div className="flex flex-row mb-3">
                    <div>
                        Player 1: {props.matchData.player_1?.name}
                        {props.commandState.p1Submitted ? (
                            <div className="text-green-600">
                                <ThickCheckIcon />
                            </div>
                        ) : (
                            ''
                        )}
                    </div>
                    <div className="pl-8 pr-8" />
                    <div>
                        Player 2: {props.matchData.player_2?.name}
                        {props.commandState.p2Submitted ? (
                            <div className="text-green-600">
                                <ThickCheckIcon />
                            </div>
                        ) : (
                            ''
                        )}
                    </div>
                </div>
                <Board
                    {...{
                        matchData: props.matchData,
                        selectedPos,
                        highlightedPosList,
                        handlePosClick,
                        getTargetedPos,
                        replayingTurn,
                        finishReplay: () => setReplayingTurn(false)
                    }}
                />
            </div>
            <div className="flex flex-col grow-1 items-center">
                <div className="flex flex-row">
                    <div className="mr-5">
                        {selectedPos ? (
                            <DetailPanel
                                {...{
                                    position: selectedPos,
                                    creatureState: selectedPos.creature_state_id
                                        ? getMatchCreatureState(
                                              props.matchData,
                                              selectedPos.creature_state_id
                                          )
                                        : null
                                }}
                            />
                        ) : (
                            ''
                        )}
                    </div>
                    {props.playerData && props.matchData.player_2 ? (
                        <div>
                            <OrderPanel
                                {...{
                                    currentPlayer: props.playerData,
                                    matchData: props.matchData,
                                    commandMode,
                                    commands,
                                    submitted: playerCommandState,
                                    updateCommand,
                                    selectedPos,
                                    setCommandMode,
                                    boxClickFunc: handleOrderBoxClick
                                }}
                            />
                            <div>Note: actions happen before moves</div>
                        </div>
                    ) : (
                        ''
                    )}
                </div>
            </div>
            <div className="flex flex-col">
                <Button onClick={() => refreshMatch()}>Refresh Match Data</Button>
                <div className="mb-2" />
                <Button onClick={() => setReplayingTurn(true)}>Rewatch Turn</Button>
            </div>
        </div>
    )
}

const fillBlankCommands = (matchData: MatchData, playerName: string): CommandData[] => {
    const playerData = getActivePlayer(playerName, matchData)
    const playerCreatureStates = matchData.creature_states.filter(
        (cs) => cs.creature.player_id === playerData?.id
    )
    return playerCreatureStates.map((cs) => {
        return { action: null, action_target: null, creature_state_id: cs.id, move_target: null }
    })
}
