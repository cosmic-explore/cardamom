import { PositionData } from '../DataTypes'

export const arePositionsSame = (pos1: PositionData, pos2: PositionData): boolean => {
    return pos1.x === pos2.x && pos1.y === pos2.y
}
