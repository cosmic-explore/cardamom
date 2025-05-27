import { useEffect, useState } from 'react'
import {
    ActionData,
    CommandData,
    CreatureData,
    MatchData,
    PlayerData,
    PositionData
} from '../DataTypes'
import { Board } from './Board'
import { Button } from '@radix-ui/themes'
import { OrderPanel } from './OrderPanel'
import { DetailPanel } from './DetailPanel'
import {
    getActionAffected,
    getActionTargets,
    getCreatureMoveRoute,
    getCreatureMoves,
    refreshMatch
} from '../utils/server-connection'
import { arePositionsSame, getActivePlayer, getMatchCreature } from '../utils/game-utils'

const fillBlankCommands = (matchData: MatchData, playerName: string): CommandData[] => {
    // TODO: replace this with loading the commands stored by the server
    const playerData = getActivePlayer(playerName, matchData)
    return playerData
        ? playerData.creatures.map((c) => {
              return { action: null, action_target: null, creature: c, move_target: null }
          })
        : []
}

export const MatchPanel = (props: { matchData: MatchData; playerData: PlayerData }) => {
    const [selectedPos, setSelectedPos] = useState<PositionData | null>(null)
    const [highlightedPosList, setHighlightedPosList] = useState<PositionData[]>([])
    const [commandMode, setCommandMode] = useState<string>('move')
    const [commands, setCommands] = useState<CommandData[]>(
        fillBlankCommands(props.matchData, props.playerData.name)
    )

    useEffect(() => {
        updatePositionHighlights()
    }, [selectedPos, commandMode, commands])

    useEffect(() => {
        // runs only when there is an update for the match
        setCommands(fillBlankCommands(props.matchData, props.playerData.name))
        setSelectedPos(null)
        updatePositionHighlights()
    }, [props.matchData])

    const updatePositionHighlights = () => {
        // TODO: use action id instead of name
        // highlight the appropriate positions if a creature is selected
        setHighlightedPosList([])

        if (selectedPos?.creature_id != null) {
            const creature = getCreatureFromId(selectedPos.creature_id)
            const targetedPos = getTargetedPos()
            if (commandMode === 'move') {
                if (targetedPos === null) {
                    // ask the server for the possible moves
                    getCreatureMoves(creature.id).then((response) => {
                        setHighlightedPosList(response)
                    })
                } else {
                    getCreatureMoveRoute(creature.id, {
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
                    getActionTargets(creature.id, currentAction.name).then((response) => {
                        setHighlightedPosList(response)
                    })
                } else {
                    // show all the positions that will be affected by the action
                    getActionAffected(creature.id, currentAction.name, {
                        target_x: targetedPos?.x.toString(),
                        target_y: targetedPos.y.toString()
                    }).then((response) => {
                        setHighlightedPosList(response)
                    })
                }
            }
        }
    }

    const getCreatureFromId = (creatureId: string): CreatureData => {
        const creature = getMatchCreature(props.matchData, creatureId)
        if (creature) {
            return creature
        } else {
            throw new Error(`Could not find creature with ID ${creatureId} in match!`)
        }
    }

    const getTargetedPos = (): PositionData | null => {
        if (!selectedPos?.creature_id) {
            return null
        } else {
            const command = getCreatureCommand(getCreatureFromId(selectedPos.creature_id))
            return commandMode === 'move' ? command.move_target : command.action_target
        }
    }

    const getCurrentAction = (): ActionData | null => {
        if (!selectedPos?.creature_id) {
            return null
        } else {
            return getCreatureCommand(getCreatureFromId(selectedPos.creature_id)).action
        }
    }

    const getCreatureCommand = (creature: CreatureData): CommandData => {
        let command = commands.find((c) => c.creature.id === creature.id)
        if (!command) {
            command = {
                creature,
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

        const newCommands = commands.filter((c) => c.creature.id !== updatingCommand.creature.id)
        newCommands.push(updatingCommand)
        setCommands(newCommands)
    }

    const isOwnedCreature = (creature_id: string): boolean => {
        return props.playerData.creatures.some((c) => c.id === creature_id)
    }

    const isPositionIn = (pos: PositionData, posList: PositionData[]): boolean => {
        return posList.some((p) => arePositionsSame(p, pos))
    }

    const handlePosClick = async (posData: PositionData) => {
        // if the position of one of the player's creatures is selected, set a target of its
        // command if the clicked position is within the command's range
        if (selectedPos?.creature_id && isOwnedCreature(selectedPos.creature_id)) {
            const command = getCreatureCommand(getCreatureFromId(selectedPos.creature_id))
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

    const handleOrderBoxClick = (creature: CreatureData) => {
        creature.position.creature_id = creature.id
        setSelectedPos(creature.position)
    }

    return (
        <div className="flex flex-row">
            <div className="flex flex-col items-center">
                <div className="mb-1">{props.matchData.id}</div>
                <div>Turn {props.matchData.turn_number}</div>
                <div className="flex flex-row mb-3">
                    <div>Player 1: {props.matchData.player_1?.name}</div>
                    <div className="pl-8 pr-8" />
                    <div>Player 2: {props.matchData.player_2?.name}</div>
                </div>
                <Board
                    {...{
                        matchData: props.matchData,
                        selectedPos,
                        highlightedPosList,
                        handlePosClick,
                        getTargetedPos
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
                                    creature: getMatchCreature(
                                        props.matchData,
                                        selectedPos.creature_id
                                    )
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
            <Button onClick={() => refreshMatch()}>Refresh Match Data</Button>
        </div>
    )
}
