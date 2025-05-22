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
    getCreatureMoves,
    refreshMatch
} from '../utils/server-connection'
import { arePositionsSame } from '../utils/game-utils'

export const MatchPanel = (props: { matchData: MatchData; playerData: PlayerData }) => {
    const [selectedPos, setSelectedPos] = useState<PositionData | null>(null)
    const [highlightedPosList, setHighlightedPosList] = useState<PositionData[]>([])
    const [commandMode, setCommandMode] = useState<string>('move')
    const [currentAction, setCurrentAction] = useState<ActionData | null>(null)
    const [commands, setCommands] = useState<CommandData[]>([])

    useEffect(() => {
        updatePositionHighlights()
    }, [selectedPos])

    useEffect(() => {
        updatePositionHighlights()
    }, [commandMode])

    const updatePositionHighlights = () => {
        // highlight the appropriate positions if a creature is selected
        const creature = selectedPos?.creature
        if (creature != null) {
            if (commandMode === 'move') {
                // ask the server for the possible moves
                getCreatureMoves(creature.nickname).then((response) => {
                    setHighlightedPosList(response)
                })
            } else {
                // commandMode === 'action'
                setHighlightedPosList([])
                const targetedPos = getTargetedPos()

                const actionName = 'test attack'
                if (targetedPos === null) {
                    // show all the positions in range to target
                    getActionTargets(creature.nickname, actionName).then((response) => {
                        setHighlightedPosList(response)
                    })
                } else {
                    // show all the positions that will be affected by the action
                    getActionAffected(creature.nickname, actionName, {
                        target_x: targetedPos?.x.toString(),
                        target_y: targetedPos.y.toString()
                    }).then((response) => {
                        setHighlightedPosList(response)
                    })
                }
            }
        } else {
            setHighlightedPosList([])
        }
    }

    const getTargetedPos = (): PositionData | null => {
        if (!selectedPos?.creature) {
            return null
        } else {
            const command = getCreatureCommand(selectedPos.creature)
            return commandMode === 'move' ? command.move_target : command.action_target
        }
    }

    const getCreatureCommand = (creature: CreatureData): CommandData => {
        // TODO: use creature id instead of nickname
        let command = commands.find((c) => c.creature.nickname === creature.nickname)
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

    const updateCommandTarget = (updatingCommand: CommandData, newTarget: PositionData | null) => {
        // removes the existing command for a creature and inserts the new one
        // TODO: use creature id instead of nickname
        if (commandMode === 'move') {
            updatingCommand.move_target = newTarget
        } else {
            // commandMode = 'action'
            updatingCommand.action_target = newTarget
        }

        const newCommands = commands.filter(
            (c) => c.creature.nickname !== updatingCommand.creature.nickname
        )
        newCommands.push(updatingCommand)
        setCommands(newCommands)
    }

    const isOwnedCreature = (creature: CreatureData): boolean => {
        // TODO: use creature id instead of nickname
        return props.playerData.creatures.some((c) => c.nickname === creature.nickname)
    }

    const isPositionIn = (pos: PositionData, posList: PositionData[]): boolean => {
        return posList.some((p) => arePositionsSame(p, pos))
    }

    const handlePosClick = async (posData: PositionData) => {
        // if the position of one of the player's creatures is selected, set a target of its
        // command if the clicked position is within the command's range
        if (selectedPos?.creature && isOwnedCreature(selectedPos.creature)) {
            const command = getCreatureCommand(selectedPos.creature)
            const targetedPos = getTargetedPos()

            if (targetedPos === null) {
                if (isPositionIn(posData, highlightedPosList)) {
                    // set the target
                    updateCommandTarget(command, posData)
                    return
                }
            } else if (arePositionsSame(posData, targetedPos)) {
                // clear the target
                updateCommandTarget(command, null)
                updatePositionHighlights()
                return
            }
        }

        setSelectedPos(posData)
    }

    const handleOrderBoxClick = (creature: CreatureData) => {
        creature.position.creature = creature
        setSelectedPos(creature.position)
    }

    return (
        <div className="flex flex-row">
            <div className="flex flex-col items-center">
                <div className="mb-1">{props.matchData.id}</div>
                <div className="flex flex-row mb-3">
                    <div>Player 1: {props.matchData.player_1?.name}</div>
                    <div className="pl-8 pr-8" />
                    <div>Player 2: {props.matchData.player_2?.name}</div>
                </div>
                <Board
                    {...{
                        boardData: props.matchData.board,
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
                        {selectedPos ? <DetailPanel {...selectedPos} /> : ''}
                    </div>
                    {props.playerData && props.matchData ? (
                        <div>
                            <OrderPanel
                                {...{
                                    currentPlayer: props.playerData,
                                    matchData: props.matchData,
                                    commandMode,
                                    currentAction,
                                    commands,
                                    selectedPos,
                                    boxClickFunc: handleOrderBoxClick,
                                    setCommandMode: setCommandMode
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
