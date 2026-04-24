import { Injectable } from "@nestjs/common";
import { UserService } from "./user.service";

@Injectable()
export class AuthService {
  constructor(private readonly users: UserService) {}

  async validateUser(id: string) {
    return this.users.findUser(id);
  }
}
