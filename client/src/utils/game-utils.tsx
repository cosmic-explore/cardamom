import { CreatureData, CreatureState, MatchData, PositionData } from '../DataTypes'

export const arePositionsSame = (pos1: PositionData, pos2: PositionData): boolean => {
    return pos1.x === pos2.x && pos1.y === pos2.y
}

export const getActivePlayer = (playerName: string, matchData: MatchData) => {
    // TODO: use player ids instead of names
    if (matchData.player_1?.name == playerName) {
        return matchData.player_1
    } else {
        // there are only two players
        return matchData.player_2
    }
}

export const getMatchCreature = (match: MatchData, creatureId: string): CreatureData => {
    const matchCreatures = [
        ...(match.player_1?.creatures || []),
        ...(match.player_2?.creatures || [])
    ]
    const creature = matchCreatures.find((c) => c.id === creatureId)
    if (creature === undefined) {
        throw new Error(`Could not find creature_state with ID ${creatureId} in match!`)
    } else {
        return creature
    }
}

export const getMatchCreatureState = (match: MatchData, creatureStateId: string): CreatureState => {
    const creatureState = match.creature_states.find((cs) => cs.id === creatureStateId)
    if (creatureState === undefined) {
        throw new Error(`Could not find creature_state with ID ${creatureStateId} in match!`)
    } else {
        return creatureState
    }
}
