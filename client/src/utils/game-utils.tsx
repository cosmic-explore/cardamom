import { CreatureData, MatchData, PositionData } from '../DataTypes'

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

export const getMatchCreature = (
    match: MatchData,
    creatureId: string | null
): CreatureData | null => {
    const matchCreatures = [
        ...(match.player_1?.creatures || []),
        ...(match.player_2?.creatures || [])
    ]
    const creature = matchCreatures.find((c) => c.id === creatureId)
    return creature ? creature : null
}
