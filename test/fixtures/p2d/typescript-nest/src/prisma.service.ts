import { Injectable } from "@nestjs/common";

@Injectable()
export class PrismaService {
  user = {
    findUnique: async (_query: unknown) => ({ id: "1" }),
  };
}
