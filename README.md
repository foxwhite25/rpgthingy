[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<p align="center">

  <h3 align="center">不知道应该叫啥的RPG插件</h3>

  <p align="center">
    就是一个挂机RPG罢了
    <br />
    <a href="https://github.com/foxwhite25/rpgthingy">本项目</a>
    ·
    <a href="https://github.com/foxwhite25/rpgthingy/issues">回报BUG</a>
    ·
    <a href="https://github.com/foxwhite25/rpgthingy/issues">请求功能</a>
  </p>
</p>



<!-- 目录 -->
<details open="open">
  <summary><h2 style="display: inline-block">目录</h2></summary>
  <ol>
    <li>
      <a href="#关于这个插件">关于这个插件</a>
      <ul>
        <li><a href="#特点">特点</a></li>
      </ul>
    </li>
    <li>
      <a href="#如何下载并且安装">如何下载并且安装</a>
      <ul>
        <li><a href="#必備條件">必備條件</a></li>
        <li><a href="#安装">安装</a></li>
      </ul>
    </li>
    <li><a href="#使用方法">使用方法</a></li>
    <li><a href="#未来规划">未来规划</a></li>
    <li><a href="#贡献">贡献</a></li>
    <li><a href="#协议">协议</a></li>
    <li><a href="#联系">联系</a></li>
    <li><a href="#致谢">致谢</a></li>
  </ol>
</details>



<!-- 关于这个插件 -->
## 关于这个插件
本插件包含不同的采集技能等级，熟练度，战斗（饼），养成。
### 特点

* 在开始挂机之后在结算时以显示时间计算产量，保障你的群不会被刷屏。
* 每个技能中的物品都有独立熟练度，保障你群的活跃度。




<!-- 如何安装 -->
## 如何下载并且安装

要得到一份本地副本，你只需要做以下这些简单的东西

### 必備條件

这个是一个<a href="https://github.com/Ice-Cirno/HoshinoBot/">Hoshino</a>插件，你必须要要有一个设置好的Hoshino。
* Hoshino
  ```sh
  git clone https://github.com/Ice-Cirno/HoshinoBot.git
  ```
### 安装

1. 克隆这个仓库
   ```sh
   git clone https://github.com/foxwhite25/rpgthingy.git
   ```
2. 移动到modules文件夹
3. 安装必要的Python库
4. 修改你要修改的东西(_bot.py etc)
5. 将data.db移动到/~/.hoshino/目录


<!-- USAGE EXAMPLES -->
## 使用方法
数量如果是max，将会执行最大能执行的次数

|指令|说明|
|-----|-----|
|?创建角色 [角色名] |创建角色并开始游戏|
|?改名 [角色名] |转换角色名|
|?采矿 (物品id) |采矿系统相关|
|?锻造 (物品id) |锻造系统相关|
|?商店  |查看你当前可以购买的物品|
|?购买 [物品id 或 镐子] [数量或max(max只适用于手套)]|购买物品或镐子|
|?充能列表|查看手套剩余充能|
|?康康背包|查看当前背包|
|?出售 [物品1 id] [物品1 数量或max] [物品2 id]...|将会售卖指定的物品，支持一次性售卖多种类物品|
|?查看属性|查看当前的属性和GP(之后会改，只是暂时的)|
|?查看物品 [物品id]|查看该物品的售价，名字，以及描述|
|?查看合成 [物品id]|查看该物品的合成表，以及所需技能等级|
|?装备 (物品id)|如果有物品id将会装备该物品，否则显示当前装备|
|?取消装备 [物品id]|取消装备该物品|



<!-- 未来规划 -->
## 未来规划
* 增加更多的采集技能，写一个战斗系统，加一点彩蛋之类的
* 有什么要的功能可以去issue说，也欢迎pr。

<!-- 做出你的贡献 -->
## 做出你的贡献

贡献使开源社区成为了一个令人赞叹的学习，启发和创造场所。**非常感谢你所做的任何贡献**。

1. Fork 这个项目
2. 创建你的分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的改变 (`git commit -m '加入了超棒的功能'`)
4. Push到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个PR



<!-- LICENSE -->
## 协议

根据GPL3许可证分发。有关更多信息，请参见`LICENSE`。



<!-- CONTACT -->
## 联系

狐白白 - 1725036102 

项目地址: [https://github.com/foxwhite25/rpgthingy](https://github.com/foxwhite25/rpgthingy)



<!-- ACKNOWLEDGEMENTS -->
## 致谢

* []()<a href="https://github.com/Ice-Cirno/HoshinoBot/">Hoshino</a>
* []()<a href="https://github.com/GWYOG/GWYOG-Hoshino-plugins">GWYOG-Hoshino-plugins</a>





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/foxwhite25/rpgthingy.svg?style=for-the-badge
[contributors-url]: https://github.com/foxwhite25/rpgthingy/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/foxwhite25/rpgthingy.svg?style=for-the-badge
[forks-url]: https://github.com/foxwhite25/rpgthingy/network/members
[stars-shield]: https://img.shields.io/github/stars/foxwhite25/rpgthingy.svg?style=for-the-badge
[stars-url]: https://github.com/foxwhite25/rpgthingy/stargazers
[issues-shield]: https://img.shields.io/github/issues/foxwhite25/rpgthingy.svg?style=for-the-badge
[issues-url]: https://github.com/foxwhite25/rpgthingy/issues
[license-shield]: https://img.shields.io/github/license/foxwhite25/rpgthingy.svg?style=for-the-badge
[license-url]: https://github.com/foxwhite25/rpgthingy/blob/master/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/foxwhite25
