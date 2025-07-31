export type ActionData = {
    id: string
    name: string
    reach: string
    power: number
}

export type BoardData = {
    size_x: number
    size_y: number
    columns: PositionData[][]
}

export type CommandData = {
    creature: CreatureData
    move_target: PositionData | null
    action: ActionData | null
    action_target: PositionData | null
}

export type CreatureData = {
    id: string
    species_id: string
    player_id: string
    nickname: string
    level: number
    max_hp: number
    current_hp: number
    attack: number
    speed: number
    actions: ActionData[]
    position: PositionData
}

export type MatchData = {
    id: string
    board: BoardData
    history: BoardData[][]
    player_1: PlayerData | null
    player_2: PlayerData | null
    active: boolean
    turn_number: number
}

export type PositionData = {
    x: number
    y: number
    creature_id: string | null
}

export type PlayerData = {
    id: string
    name: string
    creatures: CreatureData[]
}
